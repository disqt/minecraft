# Modpack Version Checker

## Problem

Players join the Minecraft server with outdated modpacks or no modpack at all. There's no way to notify them that an update is available.

## Solution

A Fabric client mod + Paper server plugin pair that communicates over a custom plugin messaging channel. The server compares the client's reported modpack version against the latest from `manifest.json` and sends a styled chat message if outdated or missing.

## Architecture

```
Client (Fabric mod)                    Server (Paper plugin)
┌──────────────────┐                  ┌──────────────────────┐
│ Read version from│   disqt:version  │ Listen on channel    │
│ modpack-version  │ ──────────────>  │ Compare to latest    │
│ .txt on join     │                  │ Send message if      │
└──────────────────┘                  │ outdated/missing     │
                                      │                      │
                                      │ Fetch manifest.json  │
                                      │ periodically         │
                                      └──────────────────────┘
```

## Source Location

```
modpack-version-checker/
  fabric-mod/           # Fabric client mod (Java)
    src/
    build.gradle.kts
  paper-plugin/         # Paper server plugin (Java)
    src/
    build.gradle.kts
```

Both live in this repo (`disqt/minecraft`).

### Target Versions

- Minecraft: 1.21.11
- Fabric Loader: latest stable
- Fabric API: latest for 1.21.11
- Paper API: 1.21.11 (uses `paper-plugin.yml`)
- Java: 21

## Fabric Mod (`disqt-version`)

- Registers custom payload type for channel `disqt:version` during mod initialization
- On server join (`ClientPlayConnectionEvents.JOIN`), reads `modpack-version.txt` from the game directory (`.minecraft/modpack-version.txt`), trims whitespace
- Sends the version string (e.g. `2.2`) as a UTF-8 payload to the server via `ClientPlayNetworking.send()`
- If file is missing, sends nothing (behaves as if no modpack installed)
- No dependencies beyond Fabric API networking module
- Single class, minimal footprint

### modpack-version.txt

Plain text file containing just the version string, e.g.:
```
2.2
```

This file is included in the modpack zip. Updated when creating new versions -- no mod rebuild needed.

## Paper Plugin (`DisqtVersion`)

### Join Flow

1. Player joins the server (`PlayerJoinEvent`)
2. Server starts a 5-second delayed task (100 ticks) for that player
3. If `disqt:version` plugin message arrives within 5s:
   - Cancel the delayed task
   - Compare received version against cached latest version
   - If outdated: send outdated message, then send each changelog line (if any)
   - If current: do nothing
4. If no message after 5s:
   - Send no-modpack message

### Manifest Fetching

- On plugin enable: fetch `https://disqt.com/minecraft/modpack/manifest.json`
- Extract `latest.version` (e.g. `"1.21.11 v2.2"`) and `latest.changelog` (array of strings)
- Cache both in memory
- Refresh every 30 minutes (configurable)
- If fetch fails, keep using last cached value

### Configuration

`config.yml`:
```yaml
manifest-url: "https://disqt.com/minecraft/modpack/manifest.json"
refresh-minutes: 30
changelog-lines: 3
messages:
  outdated: "<black>[</black><green>D</green><gold>i</gold><black>s</black><green>q</green><gold>t</gold><black>]</black> <gray>Modpack update available:</gray> <aqua>v{latest}</aqua> <gray>-</gray> <green>disqt.com/minecraft</green>"
  changelog-line: "  <gray>- {line}</gray>"
  no-modpack: "<black>[</black><green>D</green><gold>i</gold><black>s</black><green>q</green><gold>t</gold><black>]</black> <gray>Get the modpack at</gray> <green>disqt.com/minecraft</green>"
```

`{latest}` is replaced with the version string. `{line}` is replaced with each changelog entry.

### Version Comparison

The manifest `latest.version` field is `"1.21.11 v2.2"`. The client sends just `"2.2"`. The plugin extracts the version suffix from the manifest (everything after the last space + `v`, e.g. `"v2.2"` -> `"2.2"`) for comparison. Both sides are trimmed of whitespace. Simple string equality -- if they don't match, the client is outdated.

## Deployment

### Client
- Build the Fabric mod JAR
- Place it in the modpack's `mods/` folder
- Create/update `modpack-version.txt` in `.minecraft/`
- Both are included when zipping and pushing the modpack

### Server
- Build the Paper plugin JAR
- SCP to `/home/minecraft/serverfiles/plugins/`
- Restart server

## Manifest Changelog Field

Add a `changelog` array to the `latest` entry (and each version entry) in `manifest.json`:

```json
{
  "latest": {
    "version": "1.21.11 v2.2",
    "file": "1.21.11 v2.2.zip",
    "date": "2026-03-14",
    "mc": "1.21.11",
    "modloader": "Fabric",
    "size": "200 MB",
    "changelog": [
      "Updated shaders and performance mods",
      "Added Ping Wheel mod"
    ]
  }
}
```

Full changelog, ordered by importance. Two sources:

1. **Skill-driven update** (`/prism-audit`) -- version-refresh already gathers per-mod changelogs (Step 2.5) and consolidates them into the upgrade plan. Two small skill changes:
   - **version-refresh**: after user approves the upgrade plan, write a `## Changelog summary` section to the decision doc with all notable changes ordered by importance (no line limit)
   - **executor Step 12d**: read `## Changelog summary` from the decision doc and include it as a `"changelog"` array in the manifest entry
2. **Manual push** -- user provides changelog lines when updating manifest, or omits the field (plugin handles missing changelog gracefully).

The manifest stores the **full** changelog. The Paper plugin controls how many lines to display (default 3, configurable).

## Future Considerations

- The `modpack-version.txt` update could be automated in the zip/push process
- Could make the link clickable in chat (MiniMessage `<click:open_url:...>`)
