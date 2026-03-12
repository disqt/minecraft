# CLAUDE.md

## What This Is

A Claude Code **plugin marketplace** (`disqt/minecraft`) for Minecraft server and modpack management. Not a traditional codebase — contains no buildable source code. Everything here is skill definitions, agent prompts, and plugin metadata that Claude Code consumes directly.

## Repository Structure

```
.claude-plugin/marketplace.json   # Marketplace registry — lists installable plugins
redstone-viewer/                  # Deployed HTML viewers (served at disqt.com/minecraft/redstone/)
plugins/
  minecraft-prism-client/         # Client-side modpack management (v1.0.0)
    .claude-plugin/plugin.json    # Plugin metadata
    agents/
      mc-category-agent.md        # Agent definition for parallel category audits
    skills/
      prism-audit/SKILL.md        # Entry point: full modset refresh (meta + version + executor)
      meta-refresh/               # Phase 1: are mods still best-in-class?
        SKILL.md                  # Orchestrator — dispatches parallel category agents
        category-agent-prompt.md  # Template injected into each category agent
        config-research-agent.md  # Agent spec for post-install config tuning
        upgrade-plan-format.md    # Output format for meta upgrade plans
      version-refresh/            # Phase 2: are mods up to date?
        SKILL.md                  # Orchestrator — dispatches parallel version agents
        version-agent-prompt.md   # Per-mod version lookup procedure
        changelog-agent-prompt.md # Per-mod changelog extraction
        version-upgrade-plan-format.md
        executor-agent-spec.md    # Background agent: clone, download, boot-verify, publish
        download-agent-prompt.md  # Per-mod download agent
        boot-verification-agent.md
      compat-check/SKILL.md       # Verifies exact MC version builds via Modrinth API
      redstone/                   # Redstone circuit build guides with layer viewer
        SKILL.md                  # Skill entry point
        assets/                   # HTML viewer templates (2D + 3D)
        references/               # Component docs, circuit catalog, Java mechanics
      redstone-workspace/         # Skill development: evals and iteration results
  minecraft-papermc-server/       # Server-side plugin management (v1.0.0)
    .claude-plugin/plugin.json    # Plugin metadata
    agents/
      server-category-agent.md    # Agent definition for parallel category audits
    skills/
      papermc-audit/SKILL.md      # Entry point: gather inputs, create decision doc, chain to paper-check
      paper-check/                # Phase 1: can PaperMC be upgraded?
        SKILL.md                  # Query PaperMC API, run compat-check on all plugins
        paper-compat-report-format.md
      meta-refresh/               # Phase 2: are plugins still best-in-class?
        SKILL.md                  # Orchestrator — dispatches parallel category agents
        category-agent-prompt.md  # Per-category research with Hangar-first API + wildcards
        config-research-agent.md  # Post-install config tuning for server plugins
        upgrade-plan-format.md    # Output format with wildcards section
      version-refresh/            # Phase 3: are plugins up to date?
        SKILL.md                  # Orchestrator — dispatches parallel version agents
        version-agent-prompt.md   # Per-plugin version lookup (Hangar-first)
        changelog-agent-prompt.md # Per-plugin changelog extraction
        version-upgrade-plan-format.md
      executor/                   # Phase 4: staging verification + production cutover
        SKILL.md                  # Foreground skill: staging, downloads, verify, cutover
        download-agent-prompt.md  # Per-plugin download to staging via SSH
        staging-verification-agent.md  # Boot-test on staging server
        cutover-agent-prompt.md   # Production cutover with backup + rollback
        changelog-digest-format.md
      compat-check/SKILL.md       # Verifies builds via Hangar/Modrinth API
```

## Architecture

### Client plugin (minecraft-prism-client)

Three-phase pipeline, each phase chaining to the next:

1. **prism-audit** (entry point) — creates a decision doc, then invokes meta-refresh
2. **meta-refresh** — categorizes mods, dispatches parallel category agents (one per category), synthesizes results into an upgrade plan, writes approved decisions to the doc, then chains to version-refresh
3. **version-refresh** — dispatches parallel version-check agents (one per mod), builds upgrade plan, writes approved decisions, then dispatches a background executor agent

The **executor** clones the Prism instance, applies all approved changes (downloads, removals, config), boot-verifies, and optionally publishes to VPS.

### Server plugin (minecraft-papermc-server)

Four-phase pipeline with staging verification and live cutover:

1. **paper-check** — queries PaperMC API for newer versions, runs compat-check on all plugins against target version
2. **meta-refresh** — categorizes plugins, dispatches parallel category agents, surfaces wildcards, produces upgrade plan
3. **version-refresh** — dispatches parallel version/changelog agents, produces version upgrade plan
4. **executor** (foreground) — prepares staging server, downloads plugins, researches configs, boot-verifies on staging, then cuts over to production with player warning and LGSM backup/rollback safety

### Shared design constraints

- **Read-only until user approval** — no files are written until the user explicitly approves the upgrade plan
- **compat-check is mandatory** — every verdict and gap recommendation must have verified API compatibility. Search facets use minor-series matching, not exact-version matching
- **Vanilla+ profile** — never recommend minimap, world map, block/entity info overlays, or mods/plugins revealing non-vanilla information. Server: no economy, minigames, custom enchantments
- **Host-agnostic paths** — client skills detect OS and resolve `{PRISM_INSTANCES}` and `{PRISM_EXE}` at runtime. Server skills use runtime SSH inputs. Never hardcode OS-specific or host-specific paths

## Skill Invocations

### Client (minecraft-prism-client)

| Slash command | Skill |
|---------------|-------|
| `/prism-audit` | Full client audit (meta-refresh + version-refresh + executor) |
| `/meta-refresh` | Meta-only: find better mods, gaps, redundancies |
| `/version-refresh` | Version-only: check all mods for updates |
| `/compat-check` | Internal sub-procedure (not user-invoked) |
| `/redstone` (WIP) | Redstone circuit build guides with HTML layer viewer |

### Server (minecraft-papermc-server)

| Slash command | Skill |
|---------------|-------|
| `/papermc-audit` | Full server audit (paper-check + meta-refresh + version-refresh + executor) |
| `/paper-check` | Can PaperMC be upgraded? Which plugins break? |
| `/meta-refresh` | Are these the right plugins? Gaps, replacements, wildcards |
| `/version-refresh` | Are all plugins up to date? |
| `/compat-check` | Internal sub-procedure (not user-invoked) |

## Docs

| Topic | File |
|-------|------|
| Redstone skill (in-progress) | `docs/in-progress-redstone-skill.md` |
| 3D voxel viewer plan | `docs/plans/2026-03-10-3d-voxel-viewer.md` |

## Deploy

- **Redstone viewer**: `scp <file> dev:/home/dev/redstone-viewer/` — served at `https://disqt.com/minecraft/redstone/`
- Nginx: `location /minecraft/redstone/` aliases `/home/dev/redstone-viewer/`

## Key APIs Used

- **Modrinth API v2** (`https://api.modrinth.com/v2/`) — primary source for client mod search, version lookup, compatibility verification, and reference pack contents
- **Hangar API v1** (`https://hangar.papermc.io/api/v1/`) — primary source for server plugin search, version lookup, and compatibility verification
- **PaperMC API v2** (`https://api.papermc.io/v2/`) — Paper version checks and build downloads
- **CurseForge / GitHub** — fallback sources when mods/plugins aren't on Modrinth or Hangar

## Decision Doc

- **Client:** `./minecraft-audits/prism-<instance>-YYYY-MM-DD.md` — contract between client phases (meta-refresh writes `## Meta decisions`, version-refresh appends `## Version decisions`, executor reads both)
- **Server:** `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` — contract between server phases (paper-check writes `## Paper decisions`, meta-refresh writes `## Meta decisions`, version-refresh writes `## Version decisions`, executor reads all and appends `## Execution summary`)
