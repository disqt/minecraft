# CLAUDE.md

## What This Is

A Claude Code **plugin marketplace** (`disqt/minecraft`) for Minecraft server and modpack management. Not a traditional codebase — contains no buildable source code. Everything here is skill definitions, agent prompts, and plugin metadata that Claude Code consumes directly.

## Repository Structure

```
.claude-plugin/marketplace.json     # Marketplace registry
redstone-viewer/                    # HTML viewers (disqt.com/minecraft/redstone/)
modpack-version-checker/            # Modpack version checker (Paper plugin + Fabric mod)
plugins/
  minecraft-prism-client/           # Client modpack management (v1.0.3) — skills: prism-audit, meta-refresh, version-refresh, compat-check, redstone
  minecraft-papermc-server/         # Server plugin management (v1.0.3) — skills: papermc-audit, paper-check, meta-refresh, version-refresh, executor, compat-check
  minecraft-spark-analyzer/         # Spark profiler analysis (v1.0.0) — skill: spark-analyze
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

## Deploy

- **Chunk inspector**: `disqt.com/minecraft/chunks/` — Astro page in `disqt-minecraft` project. Data generated by `scripts/generate-chunk-data.py`, served from `/home/dev/minecraft-maps/data/`
- **Redstone viewer**: `scp <file> dev:/home/dev/redstone-viewer/` — served at `https://disqt.com/minecraft/redstone/`
- Nginx: `location /minecraft/redstone/` aliases `/home/dev/redstone-viewer/`
- **Backup archives:** `C:\Users\leole\OneDrive\pmc_backup\` (tar.zst, cloud-synced — do NOT stream-read directly, copy local first)

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
**Important:** `7z` is available (installed via choco). Python `zipfile` also works.

### Prism Launcher Instances
- Path: `C:\Users\leole\AppData\Roaming\PrismLauncher\instances\`
- Current modpack: `1.21.11 v2.6` (Fabric 0.18.4, MC 1.21.11, 144 mods)
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

### Known Issues

#### Distant Horizons log spam (v2.4.4b+)
`onWorldGenTaskComplete` NullPointerException spams ~45k times per session. Known regression (GitLab #1212), introduced in 2.4.4b. Not fixed yet. Silence via `DistantHorizons.toml`:
- `logWorldGenEvent = "DISABLED"`, `logWorldGenLoadEvent = "DISABLED"`, `logWorldGenPerformance = "DISABLED"`
- `logWorldGenEventToFile = "ERROR"`, `logWorldGenChunkLoadEventToFile = "ERROR"`
- `overrideVanillaGLLogger = false` (suppresses Iris+DH GL texture error stacktrace)
- Do NOT downgrade to 2.4.3b -- loses stutter fix for chunk border crossing

#### Spark swap false alarm on Windows
Spark reports Windows page file *allocated* size as "swap used", not actual usage. A "38 GB swap" reading is normal — check actual usage with `Get-CimInstance Win32_PageFileUsage` (CurrentUsage field). Only flag if CurrentUsage is high.

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
