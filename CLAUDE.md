# CLAUDE.md

## What This Is

A Claude Code **plugin marketplace** (`disqt/minecraft`) for Minecraft server and modpack management. Not a traditional codebase — contains no buildable source code. Everything here is skill definitions, agent prompts, and plugin metadata that Claude Code consumes directly.

## Repository Structure

```
.claude-plugin/marketplace.json   # Marketplace registry — lists installable plugins
redstone-viewer/                  # Deployed HTML viewers (served at disqt.com/minecraft/redstone/)
plugins/
  minecraft-prism-client/         # Client-side modpack management (v1.0.3)
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
  minecraft-papermc-server/       # Server-side plugin management (v1.0.3)
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
  minecraft-spark-analyzer/       # Spark profiler report analysis (v1.0.0)
    .claude-plugin/plugin.json    # Plugin metadata
    skills/
      spark-analyze/              # Analyze spark.lucko.me profiles for FPS/TPS issues
        SKILL.md                  # Skill entry point: fetch, parse, diagnose, recommend
        scripts/
          analyze_spark.py        # Bundled parser: fetches JSON, computes per-mod hotspots
        references/
          diagnosis-patterns.md   # FPS diagnosis catalog, JVM args, mod recommendations
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
4. **executor** (foreground) — prepares staging server, downloads plugins, researches configs, boot-verifies on staging, then offers cutover: apply now, push to `plugins/update/` folder, or abandon

### Shared design constraints

- **Read-only until user approval** — no files are written until the user explicitly approves the upgrade plan
- **compat-check is mandatory** — every verdict and gap recommendation must have verified API compatibility. Search facets use minor-series matching, not exact-version matching
- **Vanilla+ profile** — never recommend minimap, world map, block/entity info overlays, or mods/plugins revealing non-vanilla information. Server: no economy, minigames, custom enchantments
- **Host-agnostic paths** — client skills detect OS and resolve `{PRISM_INSTANCES}` and `{PRISM_EXE}` at runtime. Server skills use runtime SSH inputs. Never hardcode OS-specific or host-specific paths
- **Numbered prompts** — all user-facing choices use numbered options (e.g. `1. **Proceed** 2. **Cancel**`), never yes/cancel or A/B letters

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

### Spark analyzer (minecraft-spark-analyzer)

| Slash command | Skill |
|---------------|-------|
| `/spark-analyze` | Analyze a spark.lucko.me profile for FPS/TPS issues |

## Docs

| Topic | File |
|-------|------|
| Redstone skill (in-progress) | `docs/in-progress-redstone-skill.md` |
| 3D voxel viewer plan | `docs/plans/2026-03-10-3d-voxel-viewer.md` |

## Deploy

- **Redstone viewer**: `scp <file> dev:/home/dev/redstone-viewer/` — served at `https://disqt.com/minecraft/redstone/`
- Nginx: `location /minecraft/redstone/` aliases `/home/dev/redstone-viewer/`

## Modpack Publishing

Quick-publish a new modpack version to `disqt.com/minecraft/modpack/`:

1. Copy instance, update `instance.cfg` (name, ExportVersion), `modpack-version.txt`
2. Zip with Python (no `zip`/`7z` on this Windows machine):
   ```python
   python3 -c "
   import zipfile, os
   src = r'<instance-path>'
   dst = r'C:\Users\leole\AppData\Local\Temp\<name>.zip'
   exclude = ['Distant_Horizons_server_data', 'screenshots', 'saves', 'downloads', '.mixin.out', 'debug', 'logs']
   with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zf:
       for root, dirs, files in os.walk(src):
           dirs[:] = [d for d in dirs if d not in exclude]
           for f in files:
               full = os.path.join(root, f)
               arcname = '<name>/' + os.path.relpath(full, src)
               zf.write(full, arcname)
   "
   ```
3. `scp <zip> dev:/home/dev/prism/`
4. Update symlink: `ssh dev "cd /home/dev/prism && ln -sf '<name>.zip' latest.zip"`
5. Update manifest.json (prepend to versions array, update latest)
6. Cleanup (handle spaces in filenames): `ls -t *.zip | grep -v latest.zip | tail -n +4 | while IFS= read -r f; do rm -f "$f"; done`
7. Reload version checker: `ssh minecraft "tmux -S /tmp/tmux-1000/pmcserver-bb664df1 send-keys -t pmcserver 'plugman reload DisqtVersion' Enter"`

**Important:** Close Minecraft before copying instances -- locked files cause incomplete copies.
**Important:** `zip`/`7z` are not installed on this Windows machine. Use Python `zipfile` module.

### Prism Launcher Instances
- Path: `C:\Users\leole\AppData\Roaming\PrismLauncher\instances\`
- Current modpack: `1.21.11 v2.5` (Fabric 0.18.4, MC 1.21.11, 135 mods)
- JVM: Shenandoah GC with brucethemoose client-tuned flags
- Modpack hosted at: `https://disqt.com/minecraft/modpack/` (VPS path: `/home/dev/prism/`)

### DisqtVersion Plugin (modpack version checker)
- Source: `modpack-version-checker/paper-plugin/`
- Build: `cd modpack-version-checker/paper-plugin && ./gradlew build`
- JAR: `build/libs/DisqtVersion-1.0.0.jar`
- Deploy: `scp <jar> minecraft:/home/minecraft/serverfiles/plugins/` then `plugman reload DisqtVersion`
- Uses `<` version comparison (not `!=`) to avoid false positives from stale manifest cache

### Known Issues

#### Distant Horizons log spam (v2.4.4b+)
`onWorldGenTaskComplete` NullPointerException spams ~45k times per session. Known regression (GitLab #1212), introduced in 2.4.4b. Not fixed yet. Silence via `DistantHorizons.toml`:
- `logWorldGenEvent = "DISABLED"`, `logWorldGenLoadEvent = "DISABLED"`, `logWorldGenPerformance = "DISABLED"`
- `logWorldGenEventToFile = "ERROR"`, `logWorldGenChunkLoadEventToFile = "ERROR"`
- `overrideVanillaGLLogger = false` (suppresses Iris+DH GL texture error stacktrace)
- Do NOT downgrade to 2.4.3b -- loses stutter fix for chunk border crossing

## Key APIs Used

- **Modrinth API v2** (`https://api.modrinth.com/v2/`) — primary source for client mod search, version lookup, compatibility verification, and reference pack contents
- **Hangar API v1** (`https://hangar.papermc.io/api/v1/`) — primary source for server plugin search, version lookup, and compatibility verification
- **PaperMC API v2** (`https://api.papermc.io/v2/`) — Paper version checks and build downloads
- **CurseForge / GitHub** — fallback sources when mods/plugins aren't on Modrinth or Hangar

## Version Bumps

Any change to a plugin's skills, agents, or prompts **must** include a version bump. Use semver: patch for fixes/tweaks, minor for new features or behaviour changes, major for breaking changes.

When bumping a plugin version, update all three locations:
1. `plugins/<name>/.claude-plugin/plugin.json`
2. `.claude-plugin/marketplace.json`
3. The version shown in the repository structure tree above

## Decision Doc

- **Client:** `./minecraft-audits/prism-<instance>-YYYY-MM-DD.md` — contract between client phases (meta-refresh writes `## Meta decisions`, version-refresh appends `## Version decisions`, executor reads both)
- **Server:** `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` — contract between server phases (paper-check writes `## Paper decisions`, meta-refresh writes `## Meta decisions`, version-refresh writes `## Version decisions`, executor reads all and appends `## Execution summary`)
