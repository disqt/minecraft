# PaperMC Server Plugin Management Skill — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin skill (`minecraft-papermc-server`) that audits and updates PaperMC server plugins through a four-phase pipeline: paper-check, meta-refresh, version-refresh, and executor — with staging server verification and safe live cutover.

**Architecture:** Mirrors the existing `minecraft-prism-client` plugin structure — SKILL.md orchestrators dispatch parallel agents, produce deliverables, wait for user approval, write to a shared decision doc, then chain forward. The server skill adds a Paper version check pre-flight phase and replaces the client's local instance cloning with SSH-based staging server verification and production cutover.

**Tech Stack:** Claude Code plugin system (SKILL.md, agent prompts, format specs), Hangar API v1, Modrinth API v2, PaperMC API v2, SSH/rsync for remote server management.

**Spec:** `docs/superpowers/specs/2026-03-12-papermc-server-plugin-skill-design.md`

**Reference:** `plugins/minecraft-prism-client/` — the client-side counterpart. Follow its conventions exactly for frontmatter, section structure, formatting, and naming.

---

## File Map

All paths relative to repository root (`/home/leo/documents/code/disqt.com/minecraft/`).

### Plugin metadata
| File | Responsibility |
|------|---------------|
| `plugins/minecraft-papermc-server/.claude-plugin/plugin.json` | Plugin identity and registration |

### Skills (SKILL.md orchestrators)
| File | Responsibility |
|------|---------------|
| `plugins/minecraft-papermc-server/skills/audit/SKILL.md` | Entry point — gather inputs, create decision doc, chain to paper-check |
| `plugins/minecraft-papermc-server/skills/paper-check/SKILL.md` | Paper version upgrade check — query PaperMC API, run compat-check on all plugins |
| `plugins/minecraft-papermc-server/skills/meta-refresh/SKILL.md` | Plugin meta audit — categorize, dispatch category agents, synthesize, upgrade plan |
| `plugins/minecraft-papermc-server/skills/version-refresh/SKILL.md` | Plugin version check — dispatch version agents, changelog agents, upgrade plan |
| `plugins/minecraft-papermc-server/skills/executor/SKILL.md` | Staging prep, downloads, config research, boot verify, cutover, rollback |
| `plugins/minecraft-papermc-server/skills/compat-check/SKILL.md` | Safety gate — verify plugin builds exist for target MC version |

### Agent definitions
| File | Responsibility |
|------|---------------|
| `plugins/minecraft-papermc-server/agents/server-category-agent.md` | Agent type definition for parallel category audits |

### Agent prompts (templates injected into dispatched agents)
| File | Responsibility |
|------|---------------|
| `plugins/minecraft-papermc-server/skills/meta-refresh/category-agent-prompt.md` | Per-category research procedure + output format |
| `plugins/minecraft-papermc-server/skills/meta-refresh/config-research-agent.md` | Post-install config tuning for new/replaced plugins |
| `plugins/minecraft-papermc-server/skills/version-refresh/version-agent-prompt.md` | Per-plugin version lookup procedure |
| `plugins/minecraft-papermc-server/skills/version-refresh/changelog-agent-prompt.md` | Per-plugin changelog extraction |
| `plugins/minecraft-papermc-server/skills/executor/download-agent-prompt.md` | Per-plugin JAR download procedure |
| `plugins/minecraft-papermc-server/skills/executor/staging-verification-agent.md` | Boot verification on staging server |
| `plugins/minecraft-papermc-server/skills/executor/cutover-agent-prompt.md` | Production cutover procedure |

### Format specs (output templates)
| File | Responsibility |
|------|---------------|
| `plugins/minecraft-papermc-server/skills/paper-check/paper-compat-report-format.md` | Paper compatibility report deliverable format |
| `plugins/minecraft-papermc-server/skills/meta-refresh/upgrade-plan-format.md` | Meta upgrade plan deliverable format (with wildcards section) |
| `plugins/minecraft-papermc-server/skills/version-refresh/version-upgrade-plan-format.md` | Version upgrade plan deliverable format |
| `plugins/minecraft-papermc-server/skills/executor/changelog-digest-format.md` | Final changelog digest format |

### Marketplace registration
| File | Responsibility |
|------|---------------|
| `.claude-plugin/marketplace.json` | Add new plugin entry to marketplace registry |

### Project docs
| File | Responsibility |
|------|---------------|
| `CLAUDE.md` | Update with new plugin in repository structure |

---

## Chunk 1: Foundation — Plugin Scaffold + Compat Check + Audit Entry Point

Sets up the plugin, the shared safety gate, and the entry point that all other phases chain from. This chunk produces a plugin that can be installed and whose `/audit` command triggers (gathering inputs and creating the decision doc) even though the downstream phases don't exist yet.

### Task 1: Create plugin.json and register in marketplace

**Files:**
- Create: `plugins/minecraft-papermc-server/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Skill to invoke:** `skill-creator` — for validating plugin.json structure.

- [ ] **Step 1: Create plugin.json**

```json
{
  "name": "minecraft-papermc-server",
  "description": "Audit and update PaperMC server plugins — check Paper versions, find better plugins, update versions, stage-test and apply changes safely",
  "author": {
    "name": "disqt"
  }
}
```

Write to `plugins/minecraft-papermc-server/.claude-plugin/plugin.json`.

- [ ] **Step 2: Register in marketplace.json**

Add to the `plugins` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "minecraft-papermc-server",
  "source": "./plugins/minecraft-papermc-server",
  "description": "Audit and update PaperMC server plugins — check Paper versions, find better plugins, update versions, stage-test and apply changes safely",
  "version": "0.1.0"
}
```

- [ ] **Step 3: Commit**

```bash
git add plugins/minecraft-papermc-server/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: scaffold minecraft-papermc-server plugin with marketplace entry"
```

---

### Task 2: Create compat-check/SKILL.md

The shared safety gate. Adapted from the client skill's compat-check — same structure, but uses Hangar as primary source and checks Paper/Spigot/Bukkit loader compatibility.

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/compat-check/SKILL.md`
- Reference: `plugins/minecraft-prism-client/skills/compat-check/SKILL.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write compat-check SKILL.md**

Follow the client skill's compat-check exactly for structure (frontmatter → intro → Procedure → Rules → Report column → Baseline failure). Adapt content:

**Frontmatter:**
```yaml
---
name: compat-check
description: Use when verifying whether a PaperMC server plugin has a build for a specific MC version before recommending KEEP, ADD, REPLACE, or REMOVE for that plugin.
---
```

**Key differences from client compat-check:**
- Title: "PaperMC Plugin Compatibility Check"
- API lookup order: Hangar first, then Modrinth, then CurseForge/GitHub
- Hangar endpoint: `GET https://hangar.papermc.io/api/v1/projects/{slug}/versions?platform=PAPER&platformVersion={mc-version}`
- Modrinth endpoint: same as client but with `loaders=["paper","spigot","bukkit"]` (Paper is compatible with Spigot/Bukkit API — any hit counts)
- Dependency check: read `plugin.yml` `depend:` and `softdepend:` fields, not Modrinth dependency array
- For REMOVE candidates: check that no other installed plugin has a hard `depend:` on the removal target
- Baseline failure section: explain that Hangar search results don't guarantee exact-version builds, same issue as Modrinth

**Sections (same order as client):**
1. `# PaperMC Plugin Compatibility Check` — one-paragraph intro
2. `## Procedure` — Hangar lookup, Modrinth fallback, slug resolution, response reading table
3. `## Check dependencies` — ADD candidates: recursive dep check. REMOVE candidates: reverse dep check
4. `## Rules` — same status matrix (✓ exact, ~ minor, ? external, ✗ none)
5. `## Report column` — same table format
6. `## Baseline failure` — adapted explanation for server context

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/compat-check/SKILL.md
git commit -m "feat: add compat-check skill for server plugin verification"
```

---

### Task 3: Create audit/SKILL.md

Entry point. Gathers runtime inputs, creates the decision doc, chains to paper-check.

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/audit/SKILL.md`
- Reference: `plugins/minecraft-prism-client/skills/audit/SKILL.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write audit SKILL.md**

Follow the client skill's audit SKILL.md exactly for structure. Adapt content:

**Frontmatter:**
```yaml
---
name: audit
description: Use when the user wants to do a full refresh of their PaperMC server plugins in one session — check for Paper updates, audit plugin quality, update plugin versions, stage-test and apply changes safely.
---
```

**Body structure:**
```
REQUIRED SUB-SKILL: paper-check
REQUIRED SUB-SKILL: meta-refresh
REQUIRED SUB-SKILL: version-refresh

# PaperMC Server Audit

Entry point for a full server plugin refresh. Creates the shared decision doc, then invokes paper-check. The skills chain automatically: paper-check → meta-refresh → version-refresh → executor.

## Inputs

Ask for any of these not already provided:

- **Production SSH alias** — SSH alias for the live server (e.g. `minecraft`)
- **Server files path** — path to `serverfiles/` on production. Auto-detect: `ssh <alias> "ls /home/*/serverfiles/paper.jar 2>/dev/null || ls /home/*/serverfiles/server.jar 2>/dev/null"` and infer from result
- **LGSM script path** — path to LGSM entry point. Auto-detect: `ssh <alias> "ls /home/*/pmcserver 2>/dev/null || ls /home/*mcserver 2>/dev/null"`
- **Staging SSH alias** — SSH alias for the staging/test server
- **Staging files path** — path to server files on staging host
- **Staging boot command** — command to start PaperMC on staging (e.g. `java -jar paper.jar nogui`). Staging may not use LGSM
- **Staging Java path** — Java binary on staging (e.g. `java` or a full SDKMAN path)
- **Target MC version** — auto-detect from production `version_history.json`, or ask

## Flow

(ASCII diagram showing: audit → paper-check → meta-refresh → version-refresh → executor, with decision doc as shared contract)

## Step 1 — Auto-detect server state

SSH into production:
- Read `{server-files-path}/version_history.json` for current Paper version and MC version
- List `{server-files-path}/plugins/` for plugin count
- Report: "Found Paper {version} with {N} plugins on {hostname}"

## Step 2 — Create decision doc

Create `./minecraft-audits/` if it doesn't exist.
Create `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` with header:

(markdown template with hostname, date, MC version, Paper build, plugin count)

## Step 3 — Invoke paper-check

Say: "Invoking `paper-check`."
Pass all resolved inputs + decision doc path.
Paper-check chains to meta-refresh, which chains to version-refresh, which chains to executor.

## Common Mistakes

- **Skipping inputs** — always ask for any missing values. Don't assume SSH aliases or paths.
- **Wrong decision doc path** — must be `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`
- **Hardcoding host-specific paths** — all paths are runtime inputs, never hardcoded
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/audit/SKILL.md
git commit -m "feat: add audit entry point skill for server plugin pipeline"
```

---

## Chunk 2: Paper Check Phase

The new phase that doesn't exist in the client skill. Queries the PaperMC API for newer versions, runs compat-check on all plugins against the target version, produces the Paper Compatibility Report.

### Task 4: Create paper-compat-report-format.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/paper-check/paper-compat-report-format.md`
- Reference: `plugins/minecraft-prism-client/skills/meta-refresh/upgrade-plan-format.md` (for format spec conventions)

- [ ] **Step 1: Write the format spec**

Follow the client skill's upgrade-plan-format.md for structure (Format section → Rules section). Content from the design spec's "Paper Compatibility Report Format":

```markdown
# Paper Compatibility Report Format

## Format

(exact markdown template from design spec — current/target version headers, changelog highlights, plugin compatibility table with columns: #, Plugin, Current ver, Target build?, Status, Notes. Verdict section with READY/BLOCKER/ALL CLEAR)

## Status types

| Status | Meaning |
|--------|---------|
| READY | Plugin has a verified build for target MC version |
| BLOCKER | No build exists — blocks Paper upgrade |
| CHECK | Minor-series match only — needs manual verification |

## Rules

- All plugin names are hyperlinked to their Hangar/Modrinth page
- Stats from actual API calls — never guessed
- Sort: BLOCKERs first, then CHECKs, then READY
- Paper changelog highlights use same label taxonomy: [feature], [bugfix], [breaking], [perf]
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/paper-check/paper-compat-report-format.md
git commit -m "feat: add paper compatibility report format spec"
```

---

### Task 5: Create paper-check/SKILL.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/paper-check/SKILL.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write paper-check SKILL.md**

**Frontmatter:**
```yaml
---
name: paper-check
description: Use when the user wants to check if a PaperMC server can be upgraded to a newer version, and which plugins would break or need updates.
---
```

**Body structure:**
```
REQUIRED SUB-SKILL: compat-check

# PaperMC Version Check

Check whether a newer PaperMC version is available and verify all installed plugins have compatible builds for it. Produces a Paper Compatibility Report.

## Inputs

Ask for any of these not already provided:

- **Production SSH alias**
- **Server files path**
- **Decision doc path** — if passed from audit, use it. Otherwise: `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`

## Read-only phases

### Phase 1 — Read current state

SSH into production:
- Read `{server-files-path}/version_history.json` — extract current MC version and Paper build number
- List `{server-files-path}/plugins/*.jar` — build installed plugin list
- For each plugin JAR, extract version from filename or from `plugin.yml` inside the JAR:
  `ssh <alias> "cd {server-files-path} && jar -xf plugins/<plugin>.jar plugin.yml && grep '^version:' plugin.yml && rm plugin.yml"`

### Phase 2 — Query PaperMC API

GET https://api.papermc.io/v2/projects/paper/versions/

Compare against current version.

- If no newer version: report "Paper is up to date at {version}", write `## Paper decisions: no update available` to decision doc, offer to skip to meta-refresh
- If one newer version: proceed to Phase 3 with that version as target
- If multiple newer versions: present the list to the user, let them pick, then proceed

### Phase 3 — Compatibility check

For the selected target version:

1. Fetch Paper changelog: `GET https://api.papermc.io/v2/projects/paper/versions/{target}/builds` — read commit messages from builds between current and target
2. Run compat-check (read `../compat-check/SKILL.md`) against every installed plugin for the target MC version
3. Flag any plugin with `✗ none` as BLOCKER

### Phase 4 — Produce Paper Compatibility Report

Read `./paper-compat-report-format.md` for exact output format.

Present to user. Then:

- If ALL CLEAR: "All {N} plugins have builds for {target}. Approve {target} as the target version? Remaining phases will use it."
- If BLOCKERs: "{N} plugins block the upgrade: {list}. Stay on current version ({current}) and proceed to meta-refresh?"

## Write phases

### Phase 5 — Write Paper decisions

Append to decision doc:

## Paper decisions
| Decision | Value |
| Target version | {target} or {current} (staying) |
| Reason | ALL CLEAR / {N} blockers |
| Blockers | {list or none} |

### Phase 6 — Chain to meta-refresh

> Paper check complete. Decision doc updated.
> Proceed to meta-refresh? **(yes / cancel)**

If yes: invoke meta-refresh, passing decision doc path, target MC version, and all SSH/path inputs.
If cancel: ask to delete or keep decision doc.

## Failure Handling

If PaperMC API is unreachable or returns unexpected responses, invoke `superpowers:systematic-debugging`.

## Common Mistakes

- **Assuming version_history.json format** — always parse, don't assume structure. It's a JSON array of version entries.
- **Comparing version strings lexically** — MC versions like 1.21.11 vs 1.21.2 need semantic comparison (1.21.11 > 1.21.2)
- **Skipping compat-check for "obviously compatible" plugins** — run it on every plugin, no exceptions
- **Not extracting plugin versions** — needed for the report. Use `plugin.yml` inside JARs when filename doesn't contain version info
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/paper-check/SKILL.md
git commit -m "feat: add paper-check skill for PaperMC version upgrade checking"
```

---

## Chunk 3: Meta Refresh Phase

Categorizes plugins, dispatches parallel category agents, synthesizes into upgrade plan with wildcards section.

### Task 6: Create server-category-agent.md (agent definition)

**Files:**
- Create: `plugins/minecraft-papermc-server/agents/server-category-agent.md`
- Reference: `plugins/minecraft-prism-client/agents/mc-category-agent.md`

- [ ] **Step 1: Write agent definition**

Follow the client's `mc-category-agent.md` for frontmatter and structure. Key adaptations:

**Frontmatter:**
```yaml
---
name: server-category-agent
description: Audits a single PaperMC server plugin category for a meta-refresh run. Receives category name, user plugins, MC version, and Paper loader. Returns a Category Report with verdicts, gaps, wildcards, and redundancies — all with verified compatibility.
tools: WebFetch, WebSearch
skills: minecraft-papermc-server:compat-check
---
```

**Body:** Note that this agent receives inputs from the meta-refresh orchestrator (category name, user plugins in that category, MC version, API source priority) and must read `category-agent-prompt.md` for its full research procedure.

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/agents/server-category-agent.md
git commit -m "feat: add server category agent definition for parallel plugin audits"
```

---

### Task 7: Create meta-refresh/category-agent-prompt.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/meta-refresh/category-agent-prompt.md`
- Reference: `plugins/minecraft-prism-client/skills/meta-refresh/category-agent-prompt.md`

- [ ] **Step 1: Write category agent prompt**

Follow the client's category-agent-prompt.md structure. Key adaptations:

- **API source order:** Hangar first (`GET https://hangar.papermc.io/api/v1/projects?q={category-keyword}&platform=PAPER&platformVersion={mc-version}&limit=10&sort=-downloads`), then Modrinth (`GET https://api.modrinth.com/v2/search?query={keyword}&facets=[["project_type:mod","project_type:plugin"],["server_side:required","server_side:optional"],["versions:{mc-version}"]]`). Note: Modrinth uses `project_type:mod` for some server-side projects and `project_type:plugin` for others — search both
- **Loader filter:** `["paper","spigot","bukkit"]` on Modrinth (Paper is compatible with Spigot/Bukkit API)
- **No reference pack comparison** — server plugins don't have curated reference packs like REFINED. Instead, use download count + Hangar prominence as the primary signal
- **Vanilla+ exclusions:** economy plugins, minigame frameworks, custom enchantment plugins, gameplay-altering plugins. Allowed: performance, admin, permissions, world management, maps, QoL, cosmetic
- **Wildcards section:** After gap detection, surface 1-2 interesting plugins outside vanilla+ profile, clearly labeled. E.g., CoreProtect (block logging/rollback — useful for grief recovery even on vanilla+ servers)
- **Dependency check on REMOVE:** Check `plugin.yml` `depend:` fields of all other installed plugins. If another plugin hard-depends on the removal target, flag it as a conflict

**Output format — same Category Report structure as client, with added Wildcards section:**
```markdown
## Category Report: {category-name}

### Assessed plugins
| Plugin | Downloads | Last Updated | Compat | Verdict | Alternative | Pros | Cons |

### Gap recommendations
| Plugin | Downloads | Last Updated | Compat | Deps OK? | Reason to add | Link |

### Wildcards (outside vanilla+ profile)
| Plugin | Downloads | Why it's interesting | Link |

### Redundancies detected
| Plugin A | Plugin B | Overlap | Recommendation |

### Raw signals used
- Hangar top-10 for {category} + {mc-version}
- Modrinth top-10 for {category} + {mc-version}
- Compatibility verified via compat-check for all plugins and candidates
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/meta-refresh/category-agent-prompt.md
git commit -m "feat: add category agent prompt for server plugin meta audit"
```

---

### Task 8: Create meta-refresh/upgrade-plan-format.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/meta-refresh/upgrade-plan-format.md`
- Reference: `plugins/minecraft-prism-client/skills/meta-refresh/upgrade-plan-format.md`

- [ ] **Step 1: Write format spec**

Follow the client's upgrade-plan-format.md structure. Content from design spec's Upgrade Plan Format, with added Wildcards table. Include:

- Summary table (REPLACE, ADD, REMOVE, KEEP counts)
- Proposed changes table: `| # | Action | Plugin | Current | Alternative | DL | Compat | Pros | Cons | Links |`
- Wildcards table: `| # | Plugin | Category | DL | Why it's interesting | Links |`
- No changes needed section
- Rules: hyperlinks required, stats from API, sort order (REPLACE, ADD, REMOVE, KEEP)
- Wildcard numbering: W1, W2, etc. (separate namespace from main table). User says `approve W1` to promote a wildcard to ADD

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/meta-refresh/upgrade-plan-format.md
git commit -m "feat: add meta upgrade plan format with wildcards section"
```

---

### Task 9: Create meta-refresh/config-research-agent.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/meta-refresh/config-research-agent.md`
- Reference: `plugins/minecraft-prism-client/skills/meta-refresh/config-research-agent.md`

- [ ] **Step 1: Write config research agent spec**

Follow the client's config-research-agent.md structure. Adapt for server context:

- Config files live in `{server-files-path}/plugins/<PluginName>/` (not `.minecraft/config/`)
- Server plugin configs are often YAML, not TOML/JSON
- Tuning goals: optimal performance for a vanilla+ PaperMC server, minimize resource usage, sensible defaults for small community servers (5-20 players)
- Same output format as client (Config Report with settings changed, settings left at default, notes)

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/meta-refresh/config-research-agent.md
git commit -m "feat: add config research agent for server plugin tuning"
```

---

### Task 10: Create meta-refresh/SKILL.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/meta-refresh/SKILL.md`
- Reference: `plugins/minecraft-prism-client/skills/meta-refresh/SKILL.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write meta-refresh SKILL.md**

Follow the client skill's meta-refresh SKILL.md exactly for structure (frontmatter → REQUIRED SUB-SKILL → intro → Inputs → Read-only phases → Write phases → Failure Handling → Common Mistakes). Adapt content:

**Frontmatter:**
```yaml
---
name: meta-refresh
description: Use when the user wants to know if their PaperMC server plugins are still optimal, when plugins may have been superseded by better alternatives, when redundant plugins are suspected, or when gaps in plugin coverage exist for a given MC version and server profile.
---
```

**Key differences from client meta-refresh:**
- Inputs: SSH-based (production SSH alias, server files path) instead of local Prism instance
- Categories: performance, auth-security, maps-visualization, world-management, admin-tools, qol-cosmetic, library (no rendering, audio, shaders, hud-ui — those are client-side)
- Plugin discovery: `ssh <alias> "ls {server-files-path}/plugins/*.jar"` instead of reading local mods dir
- No reference pack comparison — use Hangar prominence + download count as primary signals
- Vanilla+ profile adapted for servers: no economy, no minigames, no custom enchantments
- Wildcards section in upgrade plan
- Version extraction: from filename or `plugin.yml` inside JAR
- Phase 2 dispatches `server-category-agent` (not `mc-category-agent`)
- Phase 6 chains to version-refresh (same as client)

**Meta Signal Sources (priority order):**
1. Hangar download count + prominence for target MC version — primary signal
2. Modrinth download count + `date_modified` — secondary signal
3. GitHub stars + last push date — tiebreaker

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/meta-refresh/SKILL.md
git commit -m "feat: add meta-refresh skill for server plugin auditing"
```

---

## Chunk 4: Version Refresh Phase

Dispatches parallel version and changelog agents, produces version upgrade plan.

### Task 11: Create version-refresh/version-agent-prompt.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/version-refresh/version-agent-prompt.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/version-agent-prompt.md`

- [ ] **Step 1: Write version agent prompt**

Follow the client's version-agent-prompt.md structure. Adapt:

- **Lookup order:** Hangar → Modrinth → CurseForge → GitHub → Not found (was Modrinth → CurseForge → GitHub)
- **Hangar lookup:** `GET https://hangar.papermc.io/api/v1/projects/{slug}/versions?platform=PAPER&platformVersion={mc-version}&limit=1&sort=-created`
- **Modrinth lookup:** same as client but with `loaders=["paper","spigot","bukkit"]`
- **Same status definitions:** UP_TO_DATE, UPDATE_AVAILABLE, INCOMPATIBLE, ABANDONED, NOT_FOUND
- **Same output format:** Mod Report with all fields

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/version-refresh/version-agent-prompt.md
git commit -m "feat: add version agent prompt for server plugin version lookup"
```

---

### Task 12: Create version-refresh/changelog-agent-prompt.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/version-refresh/changelog-agent-prompt.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/changelog-agent-prompt.md`

- [ ] **Step 1: Write changelog agent prompt**

Nearly identical to the client's changelog-agent-prompt.md. Only adaptation:

- **Lookup sources:** Add Hangar changelog lookup (`GET https://hangar.papermc.io/api/v1/projects/{slug}/versions/{version}` — read `description` field) before Modrinth
- **Same summarization rules and output format**

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/version-refresh/changelog-agent-prompt.md
git commit -m "feat: add changelog agent prompt for server plugin changelogs"
```

---

### Task 13: Create version-refresh/version-upgrade-plan-format.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/version-refresh/version-upgrade-plan-format.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/version-upgrade-plan-format.md`

- [ ] **Step 1: Write version upgrade plan format spec**

Nearly identical to client. Same table structure, same action types (MAJOR UPDATE, UPDATE, MINOR UPDATE, FLAG, ABANDON, CHECK DISCORD), same rules. Only change: links default to Hangar URLs when the plugin is on Hangar, Modrinth otherwise.

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/version-refresh/version-upgrade-plan-format.md
git commit -m "feat: add version upgrade plan format for server plugins"
```

---

### Task 14: Create version-refresh/SKILL.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/version-refresh/SKILL.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/SKILL.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write version-refresh SKILL.md**

Follow the client's version-refresh SKILL.md exactly for structure. Adapt:

**Frontmatter:**
```yaml
---
name: version-refresh
description: Use when the user wants to check their PaperMC server plugins for version updates, find newer builds across Hangar / Modrinth / CurseForge / GitHub, and optionally apply approved updates via staging verification.
---
```

**Key differences from client version-refresh:**
- Inputs: SSH-based (production SSH alias, server files path) instead of local Prism instance
- Step 1: Read plugins via SSH. Extract versions from filenames or `plugin.yml` inside JARs
- Step 2: Dispatch version agents using server version-agent-prompt (Hangar-first lookup)
- Step 2.5: Same changelog agent dispatch pattern
- Step 3-4: Same upgrade plan build and approval pattern
- Step 5: Write `## Version decisions` to decision doc (same as client)
- Step 6: Chain to executor skill (not a background agent — the server executor is foreground)
- Changelog results feed into the accumulated changelog digest (new for server skill)

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/version-refresh/SKILL.md
git commit -m "feat: add version-refresh skill for server plugin update checking"
```

---

## Chunk 5: Executor Phase

The most complex chunk. Staging prep, parallel downloads, config research, boot verification, cutover with player handling and rollback.

### Task 15: Create executor/download-agent-prompt.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/executor/download-agent-prompt.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/download-agent-prompt.md`

- [ ] **Step 1: Write download agent prompt**

Follow client's download-agent-prompt.md structure. Adapt:

- Downloads go to the **staging** server, not local filesystem
- Use SSH + curl: `ssh <staging-alias> "curl -L -o '{staging-plugins-path}/{filename}' '{url}'"`
- Remove old JARs on staging: `ssh <staging-alias> "rm '{staging-plugins-path}/{old-filename}'"`
- **Lookup order:** Hangar first (download URL from `GET /v1/projects/{slug}/versions/{version}` → `downloads.PAPER.downloadUrl`), then Modrinth, CurseForge, GitHub
- Same output format: `INSTALLED: {filename}` or `FAILED: {reason}`

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/executor/download-agent-prompt.md
git commit -m "feat: add download agent prompt for staging server plugin installation"
```

---

### Task 16: Create executor/staging-verification-agent.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/executor/staging-verification-agent.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/boot-verification-agent.md`

- [ ] **Step 1: Write staging verification agent**

Adapted from client's boot-verification-agent.md for server context:

**Key differences:**
- Boot command: configurable staging boot command (e.g. `cd {staging-files-path} && {staging-java-path} -Xms512M -Xmx1536M -jar paper.jar nogui`) — NOT LGSM
- All commands via SSH: `ssh <staging-alias> "..."`
- Log monitoring: `{staging-files-path}/logs/latest.log` (PaperMC log location)
- Plugin loading verification: parse `[Server thread/INFO]: [PluginName] Enabling PluginName v{version}` lines
- Crash indicators (same concept, server-specific patterns):
  - `---- Minecraft Crash Report ----`
  - `[Server thread/ERROR]` + exception
  - `Encountered an unexpected exception`
  - `Failed to start the minecraft server`
- Known harmless patterns: `[Server thread/WARN]` for deprecated API usage, `Ambiguity between arguments`, legacy material warnings
- World data absence: some plugins may log errors about missing worlds — flag as WARN, not FAIL, with note "staging server has no world data — plugin may work correctly on production"
- Kill: `ssh <staging-alias> "pkill -f 'paper.jar'"`
- Same evidence-based decision framework: PASS / WARN / FAIL
- Same output format as client boot verification

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/executor/staging-verification-agent.md
git commit -m "feat: add staging verification agent for server boot testing"
```

---

### Task 17: Create executor/cutover-agent-prompt.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/executor/cutover-agent-prompt.md`

This is new — no client equivalent. Defines the production cutover procedure.

- [ ] **Step 1: Write cutover agent prompt**

```markdown
# Server Cutover Procedure

Apply verified changes from staging to production. This is a destructive operation — a backup is mandatory before proceeding.

## Inputs

- Production SSH alias
- Staging SSH alias
- Server files path (production)
- Staging files path
- LGSM script path
- List of changes to apply (from decision doc)
- Paper JAR upgrade (yes/no + target version)

## Procedure

### Step 1 — Check player count

ssh <prod-alias> "<lgsm-script> send 'list'"
# Parse output for player count

If zero players: skip to Step 3.

### Step 2 — Warn players

ssh <prod-alias> "<lgsm-script> send 'say Server restarting in 5 minutes for plugin updates'"
# Wait 4 minutes
ssh <prod-alias> "<lgsm-script> send 'say Server restarting in 1 minute'"
# Wait 1 minute

### Step 3 — Backup

ssh <prod-alias> "<lgsm-script> backup"
# Wait for completion — this MUST succeed before proceeding
# Verify backup exists in LGSM backup dir

### Step 4 — Stop production

ssh <prod-alias> "<lgsm-script> stop"
# Wait for server to fully stop (check process)

### Step 5 — Apply changes

# NOTE: rsync does not support remote-to-remote. Execute rsync FROM production, pulling from staging.
# Alternatively, download staging files locally then upload to production.

# Sync plugins from staging to production (run on production host):
ssh <prod-alias> "rsync -avz --delete <staging-alias>:{staging-files-path}/plugins/*.jar {server-files-path}/plugins/"

# If Paper JAR upgrade:
ssh <prod-alias> "rsync -avz <staging-alias>:{staging-files-path}/paper.jar {server-files-path}/paper.jar"

# Sync config changes (only for plugins that had config research)
# For each plugin with config changes — do NOT use --delete on config dirs:
ssh <prod-alias> "rsync -avz <staging-alias>:{staging-files-path}/plugins/<PluginName>/ {server-files-path}/plugins/<PluginName>/"

### Step 6 — Start production

ssh <prod-alias> "<lgsm-script> start"

### Step 7 — Monitor boot

# Monitor {server-files-path}/logs/latest.log for 90 seconds
# Check for crash indicators (same as staging verification)
# Verify all expected plugins loaded

### Step 8 — Report

If boot succeeds: report SUCCESS with changelog digest
If boot fails: proceed to rollback

## Rollback procedure

If production fails to start after cutover:

1. ssh <prod-alias> "<lgsm-script> stop"  # Ensure fully stopped
2. Restore from LGSM backup taken in Step 3
3. ssh <prod-alias> "<lgsm-script> start"
4. Verify production is back online with original plugins
5. Report ROLLBACK with error details — user must investigate before retrying

## Output

CUTOVER: SUCCESS — {N} plugins updated, {N} added, {N} removed
  or
CUTOVER: ROLLBACK — {reason}. Production restored to pre-cutover state.

## Common Mistakes

- **Never rsync --delete on plugin config directories** — only use --delete on the plugins/ JAR directory. Config dirs contain user data (permissions, settings) that must be preserved.
- **Always verify backup completion** — if the LGSM backup fails or times out, abort the cutover. Do not proceed without a safety net.
- **Don't skip player count check** — always check before sending restart warnings. An empty server can be restarted immediately.
- **rsync is not remote-to-remote** — execute rsync from production pulling from staging, not between two remote hosts.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/executor/cutover-agent-prompt.md
git commit -m "feat: add cutover agent for safe production server updates"
```

---

### Task 18: Create executor/changelog-digest-format.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/executor/changelog-digest-format.md`

- [ ] **Step 1: Write changelog digest format**

Content from design spec's Changelog Digest Format. A format spec (pure template) for the accumulated changelog breakdown:

```markdown
# Changelog Digest Format

## Format

## Changelog Digest — <hostname> — YYYY-MM-DD

### Paper
<old version> -> <new version>
- [feature] ...
- [breaking] ...

### Plugins updated
**PluginName** old -> new
- [feature] ...
- [bugfix] ...

(repeat for each updated plugin)

### Plugins added
**PluginName** (new)
- one-line description

### Plugins removed
- PluginName — reason

### Config changes applied
| Plugin | Setting | Old | New | Reason |

## Rules

- Paper section only present if Paper version changed
- Changelog entries from changelog agents — do not fabricate
- Config changes from config-research agents
- Labels: [feature], [bugfix], [breaking], [perf] only
- Max 5 entries per plugin
- This digest is appended to the decision doc as the final section
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/executor/changelog-digest-format.md
git commit -m "feat: add changelog digest format for accumulated update summary"
```

---

### Task 19: Create executor/SKILL.md

**Files:**
- Create: `plugins/minecraft-papermc-server/skills/executor/SKILL.md`
- Reference: `plugins/minecraft-prism-client/skills/version-refresh/executor-agent-spec.md`

**Skill to invoke:** `skill-creator` — for quality and trigger testing.

- [ ] **Step 1: Write executor SKILL.md**

This is the most complex skill. Unlike the client's executor (a background agent), this is a foreground skill requiring user interaction for cutover approval.

**Frontmatter:**
```yaml
---
name: executor
description: Apply approved plugin changes to a PaperMC server — prepare staging, download plugins, research configs, boot-verify, and cut over to production with rollback safety.
---
```

**Body structure:**

```
REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents
REQUIRED SUB-SKILL: superpowers:systematic-debugging
REQUIRED SUB-SKILL: compat-check

# PaperMC Server Executor

Apply all approved changes from the decision doc. Prepares a staging server, verifies everything boots cleanly, then cuts over to production with player warning and rollback safety.

This is a FOREGROUND skill — the staging boot and cutover steps require user interaction.

## Inputs

(All passed from version-refresh or provided directly)
- Decision doc path
- Production SSH alias, server files path, LGSM script path
- Staging SSH alias, staging files path, staging boot command, staging Java path
- Target MC version

## Step 1 — Read decision doc

Read the decision doc. Collect all approved changes:
- Paper decisions (target version, if upgrading)
- Meta decisions (ADD, REPLACE, REMOVE actions)
- Version decisions (UPDATE, MAJOR UPDATE actions)

## Step 2 — Prepare staging

SSH into staging. Create server directory structure if needed.
rsync from production: plugins/, essential configs.
If Paper upgrade: download target Paper JAR from PaperMC API.
Do NOT sync world data.

## Step 3 — Dispatch parallel download agents

(One per ADD/REPLACE/UPDATE. Read ./download-agent-prompt.md. Wait for all.)

## Step 4 — Apply removals and dispatch config research agents

Delete REMOVE/REDUNDANT JARs on staging.
Dispatch parallel config-research agents for ADD/REPLACE plugins.
(Read ../meta-refresh/config-research-agent.md. Wait for all.)

## Step 5 — Boot verification

Read ./staging-verification-agent.md. Run the staging verification procedure.

If FAIL: report errors, invoke superpowers:systematic-debugging, do NOT proceed.
If WARN: present warnings, ask user "Proceed to cutover despite warnings? (yes / cancel)"
If PASS: proceed.

## Step 6 — Cutover

Present cutover options:
- **Option A: Apply now** — warn players (if any), backup, stop, apply, start
- **Option B: Prepare runbook** — generate exact commands for user to run later

If Option A: read ./cutover-agent-prompt.md, execute the procedure.
If Option B: output the commands as a runbook, do not execute.

## Step 7 — Changelog digest

Read ./changelog-digest-format.md. Compile the accumulated changelog from all phases.
Append `## Changelog digest` to decision doc.

## Step 8 — Write execution summary

Append `## Execution summary` to decision doc with:
- Staging verification result
- Cutover result (SUCCESS / ROLLBACK / DEFERRED)
- List of all changes applied
- Any warnings

## Failure Handling

Invoke superpowers:systematic-debugging on any unexpected failure.
If cutover fails: execute rollback procedure from cutover-agent-prompt.md.

## Common Mistakes

- **Syncing world data to staging** — staging only needs plugins and configs, not worlds. World data is large and unnecessary for boot verification.
- **Proceeding after backup failure** — the LGSM backup in the cutover procedure MUST succeed before stopping production. If backup fails, abort.
- **Not checking player count** — always check before sending restart warnings. Skip countdown if server is empty.
- **Rsync --delete on config dirs** — only use --delete on the plugins/ JAR directory, never on plugin config directories (would wipe existing configs)
```

- [ ] **Step 2: Commit**

```bash
git add plugins/minecraft-papermc-server/skills/executor/SKILL.md
git commit -m "feat: add executor skill for staging verification and production cutover"
```

---

## Chunk 6: Polish — CLAUDE.md Update + Final Review

### Task 20: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Skill to invoke:** `claude-md-improver` — for quality.

- [ ] **Step 1: Update CLAUDE.md**

Add the new plugin to the repository structure, skill invocations table, and any other relevant sections. Follow the existing CLAUDE.md patterns for how `minecraft-prism-client` is documented.

Add to the structure tree, slash commands table, and any architecture description.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with minecraft-papermc-server plugin"
```

---

### Task 21: Code review against spec

**Skill to invoke:** `superpowers:requesting-code-review` — review all files against the design spec.

- [ ] **Step 1: Review all created files**

Verify:
- Every file from the File Map exists
- Frontmatter is consistent across all SKILL.md files
- API source priority (Hangar > Modrinth > CurseForge > GitHub) is consistent in every file that references it
- Compat-check is referenced as REQUIRED SUB-SKILL in all phases that use it
- Decision doc path format is consistent (`./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`)
- Chaining pattern is correct (audit → paper-check → meta-refresh → version-refresh → executor)
- Common Mistakes sections exist in all SKILL.md files
- Failure Handling sections exist in all SKILL.md files
- No hardcoded host-specific paths anywhere

- [ ] **Step 2: Fix any issues found**

- [ ] **Step 3: Bump marketplace version to 1.0.0**

Update `.claude-plugin/marketplace.json` — change `minecraft-papermc-server` version from `0.1.0` to `1.0.0`.

- [ ] **Step 4: Final commit**

```bash
git add -A plugins/minecraft-papermc-server/ .claude-plugin/marketplace.json
git commit -m "fix: address code review feedback, bump to v1.0.0"
```
