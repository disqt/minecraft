# CLAUDE.md

## What This Is

A Claude Code **plugin marketplace** (`disqt/minecraft-claude-marketplace`) for Minecraft server and modpack management. Contains skill definitions, agent prompts, plugin metadata, and the `world-migration-cli` Python tool.

## Repository Structure

```
.claude-plugin/marketplace.json     # Marketplace registry
redstone-viewer/                    # HTML viewers (disqt.com/minecraft/redstone/)
modpack-version-checker/            # Modpack version checker (Paper plugin + Fabric mod)
plugins/
  minecraft-prism-client/           # Client modpack management (v1.0.4) — skills: prism-audit, meta-refresh, version-refresh, compat-check, redstone, publish-modpack
  minecraft-papermc-server/         # Server plugin management (v1.0.4) — skills: papermc-audit, paper-check, meta-refresh, version-refresh, executor, compat-check
  minecraft-spark-analyzer/         # Spark profiler analysis (v1.1.0) — skill: spark-analyze
docs/superpowers/                   # Plans and specs
world-migration-cli/                # Migration preview CLI (Python, see section below)
```

Each plugin has `skills/` (SKILL.md entry points), `agents/` (parallel agent definitions), and `.claude-plugin/plugin.json` (metadata). Explore subdirectories for full structure.

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
| PaperMC server skill plan | `docs/superpowers/plans/2026-03-12-papermc-server-plugin-skill.md` |
| Modpack version checker plan | `docs/superpowers/plans/2026-03-14-modpack-version-checker.md` |
| Modpack version checker design | `docs/superpowers/specs/2026-03-14-modpack-version-checker-design.md` |
| Chunk inspector (Leaflet) plan | `docs/superpowers/plans/2026-03-19-chunk-inspector-leaflet.md` |
| Migration preview CLI design | `docs/superpowers/specs/2026-03-21-migration-preview-cli-design.md` |
| Migration preview CLI plan | `docs/superpowers/plans/2026-03-21-migration-preview-cli.md` |
| PaperMC server skill design | `docs/superpowers/specs/2026-03-12-papermc-server-plugin-skill-design.md` |
| World migration trim tool plan | `docs/superpowers/plans/2026-03-20-world-migration-trim-tool.md` |
| World migration trim tool design | `docs/superpowers/specs/2026-03-20-world-migration-trim-tool-design.md` |
| Villager census design | `docs/superpowers/specs/2026-04-03-villager-census-design.md` |
| Villager census plan | `docs/superpowers/plans/2026-04-03-villager-census.md` |
| Villagers dashboard design | `docs/superpowers/specs/2026-04-04-villagers-dashboard-design.md` |
| Villagers dashboard plan | `docs/superpowers/plans/2026-04-04-villagers-dashboard.md` |

## Related Repos

| Repo | Description |
|------|-------------|
| `disqt/minecraft-villager-census` | Villager census Python backend + skill (extracted from this repo) |
| `disqt/minecraft-frontend` | Astro app at disqt.com/minecraft/ (villagers dashboard, chunks, landing) |

## Deploy

- **Chunk inspector**: `disqt.com/minecraft/chunks/` — Astro page in `minecraft-frontend` project. Data generated by `scripts/generate-chunk-data.py`, served from `/home/dev/minecraft-maps/data/`
- **Redstone viewer**: `scp <file> dev:/home/dev/redstone-viewer/` — served at `https://disqt.com/minecraft/redstone/`
- Nginx: `location /minecraft/redstone/` aliases `/home/dev/redstone-viewer/`
- **Backup archives:** `C:\Users\leole\OneDrive\pmc_backup\` (tar.zst, cloud-synced — do NOT stream-read directly, copy local first)

## Region File Analysis
- Can parse .mca region files to count specific block types per chunk, grouped by zone
- Download regions via `scp minecraft:/home/minecraft/serverfiles/world_new/region/r.X.Z.mca`
- Chunk-to-region: `region_x = chunk_x >> 5`, `region_z = chunk_z >> 5`
- Chunk-to-block: `block = chunk * 16`
- Watch for false matches in block name filtering (e.g., "bed" matches "bedrock" -- use `endswith("_bed")`)

## Migration Preview CLI

Python CLI at `world-migration-cli/migrate.py` for analyzing and trimming Minecraft world chunks during version migrations.

### Usage
```bash
python world-migration-cli/migrate.py ./world --threshold 120 --html preview.html  # local world
python world-migration-cli/migrate.py --host minecraft --remote-path /home/minecraft/serverfiles/world_new --html preview.html  # SSH
python world-migration-cli/migrate.py ./world --threshold 120 --dangerously-perform-the-trim  # actually trim
```

### Testing
- Run: `cd world-migration-cli && python -m pytest tests/ -v`
- 62 tests, all stdlib (no pip deps except optional `lz4` for MC 1.20.5+ chunks)
- Tests use `make_region_with_chunks()` helper from `tests/test_migrate_regions.py` to build valid .mca fixtures

### Module layout
- `migrate.py` — CLI entry point + pipeline orchestration
- `migrate_nbt.py` — minimal NBT reader (extracts InhabitedTime, DataVersion from compressed chunk data)
- `migrate_regions.py` — .mca region file parsing + chunk analysis
- `migrate_remote.py` — PaperMC/Vanilla layout detection + SSH download
- `migrate_html.py` — standalone HTML preview generator
- `migrate_raw.py` — binary overlay output for chunk inspector
- `migrate_mca.py` — MCA Selector CLI wrapper (for `--query` mode)
- `migrate_display.py` — terminal stats table + safety abort formatting

## Modpack Publishing

Automated via `prism-modpack-releaser/modpack_release.py`. Use the `/publish-modpack` skill (in minecraft-prism-client plugin) or run directly:

```bash
python prism-modpack-releaser/modpack_release.py "<instance-path>" --version <ver> [--dry-run] [--yes] [--no-notify]
```

Handles: zip (.packignore exclusions), changelog (auto-diff against VPS), SCP upload, manifest.json, symlink, prune, Discord notification via bot.
Config: `prism-modpack-releaser/modpack-release.json` (gitignored, contains channel ID and role ID). Template: `modpack-release.example.json`.
Tests: `python -m pytest prism-modpack-releaser/test_modpack_release.py` (CI runs on changes to that dir).

**Important:** Close Minecraft before running -- locked files cause incomplete zips.
**Important:** Instance must have `.packignore` in root or DH data (~800 MB) inflates the zip.

### Prism Launcher Instances
- Path: `C:\Users\leole\AppData\Roaming\PrismLauncher\instances\`
- Current modpack: `1.21.11 v2.10` (Fabric 0.18.4, MC 1.21.11)
- JVM: Shenandoah GC with brucethemoose client-tuned flags
- Modpack hosted at: `https://disqt.com/minecraft/modpack/` (VPS path: `/home/dev/prism/`)

### DisqtVersion Plugin (modpack version checker)
- Source: `modpack-version-checker/paper-plugin/`
- Build: `cd modpack-version-checker/paper-plugin && ./gradlew build`
- JAR: `build/libs/DisqtVersion-1.0.0.jar`
- Deploy: `scp <jar> minecraft:/home/minecraft/serverfiles/plugins/` then `plugman reload DisqtVersion`
- Fabric mod source: `modpack-version-checker/fabric-mod/`
- Fabric build: `cd modpack-version-checker/fabric-mod && ./gradlew build`
- Fabric JAR goes into Prism instance `mods/` folder
- Uses `<` version comparison (not `!=`) to avoid false positives from stale manifest cache

### AuthMe ReReloaded (authentication)
- Fork: HaHaWTH/AuthMeReReloaded v5.7.0-FORK-b53
- Config: `/home/minecraft/serverfiles/plugins/AuthMe/config.yml`
- Database: SQLite at `/home/minecraft/serverfiles/plugins/AuthMe/authme.db`
- Hash: SHA256 (`$SHA$salt$hash` format), min password length 5
- HIBP breach check: enabled (checks on registration and password change only, NOT on login)
- Reload: `ssh minecraft "tmux -S /tmp/tmux-1000/pmcserver-bb664df1 send-keys -t pmcserver 'authme reload' Enter"`

### Known Issues

#### Distant Horizons log spam (v2.4.4b+)
`onWorldGenTaskComplete` NullPointerException spams ~45k times per session. Known regression (GitLab #1212), introduced in 2.4.4b. Not fixed yet. Silence via `DistantHorizons.toml`:
- `logWorldGenEvent = "DISABLED"`, `logWorldGenLoadEvent = "DISABLED"`, `logWorldGenPerformance = "DISABLED"`
- `logWorldGenEventToFile = "ERROR"`, `logWorldGenChunkLoadEventToFile = "ERROR"`
- `overrideVanillaGLLogger = false` (suppresses Iris+DH GL texture error stacktrace)
- Do NOT downgrade to 2.4.3b -- loses stutter fix for chunk border crossing

#### Spark swap false alarm on Windows
Spark reports Windows page file *allocated* size as "swap used", not actual usage. A "38 GB swap" reading is normal — check actual usage with `Get-CimInstance Win32_PageFileUsage` (CurrentUsage field). Only flag if CurrentUsage is high.

## Discord Bot Notify Endpoint

The Disqt Discord bot (`disqt/disqt-discord-bot`, runs on `ssh cs`) exposes `localhost:9800/send` for sending messages from VPS scripts. Same VPS as `dev` (`debian-disqt-2001`).

```bash
curl -sf -X POST http://localhost:9800/send -H 'Content-Type: application/json' \
  -d '{"channel_id":"<id>","content":"<text>","embed":{"title":"...","description":"...","color":123}}'
```

Role pings work in `content` field (bot has permissions). Webhooks cannot ping roles.

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
