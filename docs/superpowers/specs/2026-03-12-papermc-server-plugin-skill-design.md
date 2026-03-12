# Design: PaperMC Server Plugin Management Skill

**Date:** 2026-03-12
**Status:** Approved
**Plugin:** `minecraft-papermc-server`

## Overview

A Claude Code plugin skill for auditing and updating PaperMC server plugins, analogous to the existing `minecraft-prism-client` for client-side Prism Launcher modpacks. Adds a new **Paper version check** phase and a **staging server** verification step to handle the unique constraints of live server management.

### Key constraints

- **Live server** — players may be online; minimize downtime
- **Staging verification** — boot-test all changes on a separate host before touching production
- **Host-agnostic** — no hardcoded references to specific machines; production and staging hosts configured at runtime
- **Vanilla+ philosophy** — performance, QoL, admin tools, visual enhancements only. Surface "wildcards" (interesting plugins outside the profile) for user consideration, clearly labeled
- **Read-only until approval** — no files written until the user explicitly approves each phase's upgrade plan

## Pipeline

```
/paper-check  ->  /meta-refresh  ->  /version-refresh  ->  executor
     |                 |                    |                   |
  Paper compat    Upgrade plan       Version upgrade      Staging boot
    report                              plan              + cutover
     |                 |                    |                   |
  ## Paper         ## Meta             ## Version          ## Execution
  decisions        decisions           decisions            summary
     \                 \                   /                   /
      `---------> decision doc <---------'  <----------------'
```

Each phase produces a deliverable, waits for user approval, writes decisions to the shared decision doc, then offers to chain to the next phase. `/audit` chains all four.

**Decision doc:** `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`

## Plugin Structure

```
plugins/minecraft-papermc-server/
├── .claude-plugin/plugin.json
├── agents/
│   └── server-category-agent.md
├── skills/
│   ├── audit/SKILL.md
│   ├── paper-check/
│   │   ├── SKILL.md
│   │   └── paper-compat-report-format.md
│   ├── meta-refresh/
│   │   ├── SKILL.md
│   │   ├── category-agent-prompt.md
│   │   ├── config-research-agent.md
│   │   └── upgrade-plan-format.md
│   ├── version-refresh/
│   │   ├── SKILL.md
│   │   ├── version-agent-prompt.md
│   │   ├── changelog-agent-prompt.md
│   │   └── version-upgrade-plan-format.md
│   ├── executor/
│   │   ├── SKILL.md
│   │   ├── download-agent-prompt.md
│   │   ├── staging-verification-agent.md
│   │   └── cutover-agent-prompt.md
│   └── compat-check/SKILL.md
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/audit` | Full pipeline: paper-check -> meta -> version -> executor |
| `/paper-check` | Can we upgrade PaperMC? Which plugins break? |
| `/meta-refresh` | Are these the right plugins? Gaps, replacements, wildcards |
| `/version-refresh` | Are all plugins up to date? |

## Runtime Inputs

Resolved at skill invocation, not hardcoded:

| Input | Description |
|-------|-------------|
| Production SSH alias | SSH access to the live server |
| Staging SSH alias | SSH access to the staging/test server |
| Server files path | Path to `serverfiles/` on production (e.g. `/home/minecraft/serverfiles/`) |
| Staging files path | Path to server files on staging host |
| LGSM script path | Path to LGSM entry point on production (e.g. `/home/minecraft/pmcserver`) |
| Staging boot command | Command to start PaperMC on staging (e.g. `java -jar paper.jar nogui`). Staging may not use LGSM |
| Staging Java path | Java binary on staging (e.g. `java` or a full SDKMAN path) |
| Target MC version | From paper-check or user-specified |

## API Source Priority

All phases use this lookup order:

1. **Hangar** — PaperMC's own plugin repo (primary)
2. **Modrinth** — broad coverage
3. **CurseForge** — fallback
4. **GitHub** — last resort
5. **Not found** — `✗ none`, block recommendation

## Entry Point: /audit

**Trigger:** `/audit`

The `/audit` SKILL.md gathers runtime inputs and creates the decision doc, then chains to paper-check.

**Procedure:**

1. Detect or prompt for runtime inputs (production SSH alias, staging SSH alias, server paths, staging boot command, staging Java path)
2. SSH into production to auto-detect current Paper version and MC version
3. Create decision doc: `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` with header (hostname, date, MC version, Paper build, plugin count)
4. Invoke paper-check with all resolved inputs

When invoked standalone (not via `/audit`), each phase (paper-check, meta-refresh, version-refresh) gathers its own inputs and creates the decision doc if one doesn't exist for today's date.

## Phase 1: Paper Check

**Trigger:** `/paper-check` or first phase of `/audit`

**Procedure:**

1. SSH into production, read `version_history.json` to get current Paper build
2. Query PaperMC API (`https://api.papermc.io/v2/projects/paper/versions/`) for available versions
3. If no newer version: report "up to date", write decisions, offer to skip to meta-refresh
4. If one newer version: check it automatically
5. If multiple newer versions: present the list, let user pick, then check that one
6. For the selected target version:
   - Run compat-check against every installed plugin
   - Fetch Paper's changelog between current and target build
   - Flag plugins with `✗ none` (no build for new version)
7. Produce **Paper Compatibility Report**

### Paper Compatibility Report Format

```markdown
## Paper Compatibility Report — <hostname>

### Current: Paper <version> (build <number>)
### Target:  Paper <version> (build <number>)

### Paper changelog highlights
- [feature] ...
- [breaking] ...

### Plugin compatibility
| # | Plugin | Current ver | Target build? | Status | Notes |
| 1 | AuthMe | 5.6.0 | ✓ exact | READY | |
| 2 | DHSupport | 0.12.0 | ✗ none | BLOCKER | no build for target |
| 3 | BlueMap | 5.15 | ~ minor | CHECK | minor-series match only |

### Verdict
READY: N/M plugins have builds
BLOCKER: N plugins — cannot upgrade until resolved
  — or —
ALL CLEAR: all M plugins have builds for target
```

8. User approval:
   - ALL CLEAR: "Approve target version? Remaining phases will use it."
   - BLOCKERs: "N plugins block upgrade. Stay on current and proceed to meta-refresh?"
9. Write `## Paper decisions` to decision doc
10. Chain: "Proceed to meta-refresh?"

## Phase 2: Meta Refresh

**Trigger:** `/meta-refresh` or second phase of `/audit`

Mirrors the client skill's meta-refresh.

**Procedure:**

1. SSH into production, list `plugins/` directory, read plugin JARs
2. Categorize plugins (performance, auth-security, maps-visualization, world-management, admin-tools, qol-cosmetic, library)
3. Dispatch parallel category agents — one per non-library category. Each agent:
   - Fetches top results from Hangar + Modrinth for that category
   - Runs compat-check on every existing plugin and candidate
   - Assigns verdicts: KEEP, REPLACE, REDUNDANT, ADD, INVESTIGATE
   - Surfaces 1-2 **wildcards** — interesting plugins outside vanilla+ profile, clearly labeled with a one-line pitch
4. Synthesize — merge category reports, resolve conflicts, de-duplicate
5. Produce **upgrade plan** with added wildcards section:

### Upgrade Plan Format

```markdown
## Upgrade Plan — <hostname>

### Summary
| Action | Count |
| REPLACE | N |
| ADD | N |
| REMOVE | N |
| KEEP | N |

### Proposed changes
| # | Action | Plugin | Current | Alternative | DL | Compat | Pros | Cons | Links |

### Wildcards (outside your usual profile)
| # | Plugin | Category | DL | Why it's interesting | Links |

### No changes needed (N plugins)
...
```

Wildcards are informational. User can approve individual wildcards to promote them to ADD actions, or ignore them.

6. Approval -> write `## Meta decisions` -> "Proceed to version-refresh?"

## Phase 3: Version Refresh

**Trigger:** `/version-refresh` or third phase of `/audit`

Mirrors the client skill's version-refresh.

**Procedure:**

1. SSH into production, read `plugins/` — extract plugin names and current versions. Server plugin JARs often lack version info in filenames (e.g. `EssentialsX.jar`), so fall back to extracting `version:` from `plugin.yml` inside the JAR (`jar -tf <plugin>.jar | grep plugin.yml`, then read it), or from the plugin's config directory
2. Dispatch parallel version agents — one per plugin:
   - Lookup on Hangar, then Modrinth, then CurseForge, then GitHub
   - Compare installed version against latest for target MC version
   - Return status: UP_TO_DATE, UPDATE_AVAILABLE, INCOMPATIBLE, ABANDONED, NOT_FOUND
3. Dispatch parallel changelog agents — one per UPDATE_AVAILABLE plugin:
   - Fetch changelogs between installed and latest version
   - Summarize: `[feature]`, `[bugfix]`, `[breaking]`, `[perf]`
   - Max 5 bullets per plugin
   - Results feed both the upgrade plan and the accumulated changelog digest
4. Produce **version upgrade plan**:

### Version Upgrade Plan Format

```markdown
## Version Upgrade Plan — <hostname>

### Summary
| Status | Count |
| Update available | N |
| Incompatible | N |
| Abandoned | N |
| Up to date | N |

### Proposed changes
| # | Action | Plugin | Version | Key changes | Notes |

### No changes needed (N plugins)
...
```

**Action types:** MAJOR UPDATE (1.x -> 2.x), UPDATE (minor/patch), MINOR UPDATE (channel/build change), FLAG (no target MC build), ABANDON (12+ months stale), CHECK DISCORD (not found on any source).

5. Approval -> write `## Version decisions` -> "Dispatch executor?"

## Phase 4: Executor

**Trigger:** Chained from version-refresh approval

The key differentiator from the client skill. Requires staging verification and a live cutover strategy. Unlike the client skill's executor (a background agent dispatched from version-refresh), this is a foreground skill — the staging boot and cutover steps require user interaction.

**Procedure:**

1. **Read decision doc** — collect all approved changes across all phases
2. **Prepare staging server:**
   - SSH into staging host
   - rsync production's `plugins/` and essential configs (`server.properties`, `bukkit.yml`, `spigot.yml`, `paper-world-defaults.yml`) to staging
   - If Paper upgrade approved: download target Paper JAR
   - No world data needed — staging only needs to boot, not run a playable world
3. **Dispatch parallel download agents** — one per ADD/REPLACE/UPDATE:
   - Download new JAR to staging's `plugins/` dir
   - Remove old JARs for REPLACE/REMOVE actions
4. **Dispatch parallel config-research agents** — one per ADD/REPLACE:
   - Find source repo, locate config file
   - Diff against existing config (for updates)
   - Flag required config changes, suggest optimal values for vanilla+ server
   - Write tuned configs to staging
5. **Boot verification on staging:**
   - Start PaperMC on staging using the configured staging boot command (e.g. `cd {staging-files-path} && {staging-java-path} -Xms512M -Xmx1536M -jar paper.jar nogui`)
   - Staging may not use LGSM — a raw `java -jar` invocation is the default
   - Monitor logs for crash indicators, plugin load failures
   - Verify all expected plugins loaded (parse `[Server thread/INFO]` lines for plugin enable messages)
   - Some plugins may WARN due to missing world data on staging — flag as WARN, not FAIL, with explanation
   - Report: PASS / WARN / FAIL
   - Kill staging server process
6. **If PASS or WARN (user approves), present cutover options:**
   - **Option A: Hot-swap with scheduled restart** — copy verified JARs to production `plugins/`, warn players, restart
   - **Option B: Maintenance window** — user picks a time, skill prepares exact commands
7. **On go-ahead (cutover):**
   - Check online player count via SSH (`list` console command). If zero players, skip countdown
   - If players online: send warning via LGSM console send (`say Server restarting in 5 minutes for updates`), wait countdown
   - Trigger LGSM backup on production
   - Stop production server
   - rsync verified `plugins/` (and Paper JAR if upgraded) from staging to production
   - Apply config changes
   - Start production server
   - Monitor boot log for successful startup
8. **If FAIL:** report errors, do not proceed, invoke `superpowers:systematic-debugging` if the cause is unclear
9. **Produce changelog digest** — accumulated from all phases:

### Changelog Digest Format

```markdown
## Changelog Digest — <hostname> — YYYY-MM-DD

### Paper
<old version> -> <new version>
- [feature] ...
- [breaking] ...

### Plugins updated
**PluginName** old -> new
- [feature] ...
- [bugfix] ...

### Plugins added
**PluginName** (new)
- description

### Plugins removed
- list

### Config changes applied
| Plugin | Setting | Old | New | Reason |
```

10. **Rollback on failed cutover:**
    - If production fails to start after cutover (crash indicators in boot log):
      - Immediately stop the server
      - Restore `plugins/` (and Paper JAR if upgraded) from the LGSM backup taken in step 7
      - Restart production with the original files
      - Report ROLLBACK with error details
    - The LGSM backup in step 7 is the safety net — cutover is destructive (rsync overwrites files), so the backup must succeed before proceeding
11. Write `## Execution summary` to decision doc

## Compat Check

Shared safety gate, used by all phases. Identical to the client skill's compat-check but with the server API source priority.

**Procedure:**

1. **Hangar:** `GET /v1/projects/{slug}/versions?platform=PAPER&platformVersion={mc-version}`
2. **Modrinth:** `GET /v2/project/{slug}/version?game_versions=["{mc-version}"]&loaders=["paper","spigot","bukkit"]` (Paper plugins are compatible with Spigot/Bukkit API — any hit counts)
3. **CurseForge / GitHub:** fallback sources
4. **Not found:** `✗ none`

**Results:**

| Result | Status | Action |
|--------|--------|--------|
| Exact version match | `✓ exact` | Use latest version + date |
| Minor series match only | `~ minor` | Flag as unconfirmed |
| External source only | `? external` | Note source |
| Nothing found | `✗ none` | Block — never recommend |

Rules:
- `✗ none` -> never recommend KEEP, ADD, or REPLACE
- For every ADD candidate, recursively check all required dependencies. If any dep has `✗ none`, drop the candidate
- For every REMOVE candidate, check `plugin.yml` `depend:` fields of all other installed plugins. If another plugin has a hard dependency on the removal target, flag it as a conflict and surface to the user
- Server plugins declare dependencies in `plugin.yml` (`depend:` for hard, `softdepend:` for soft). Only hard dependencies block removal

## Skill Invocations During Build

When implementing this plugin, invoke these skills at the right stages:

| When | Skill |
|------|-------|
| After design approval | `superpowers:writing-plans` — create implementation plan |
| Creating each SKILL.md | `skill-creator` — drive quality, test triggering |
| Creating agent prompts | `skill-creator` — validate agent definitions |
| After building skill files | `claude-md-improver` — update CLAUDE.md with new plugin |
| After each major phase built | `superpowers:requesting-code-review` — review against plan |
| Updating marketplace.json | `claude-md-improver` — keep registry accurate |
