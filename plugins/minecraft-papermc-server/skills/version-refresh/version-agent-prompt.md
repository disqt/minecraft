# Version Agent Prompt Template

Each agent checks one plugin's version status. Follow this procedure exactly.

---

## Lookup order

### 1. Hangar (primary)

```
GET https://hangar.papermc.io/api/v1/projects/{slug}/versions?platform=PAPER&platformVersion={mc-version}&limit=1&sort=-created
```

The `{slug}` is the project's Hangar identifier (e.g. `EssentialsX`, `LuckPerms`). Use the most recent version from the response.

### 2. Modrinth

If not found on Hangar, search Modrinth:

```
GET https://api.modrinth.com/v2/search?query=<plugin-name>&facets=[["project_type:plugin"],["versions:<mc-version>"]]
```

Take the top result's `project_id`, then:

```
GET https://api.modrinth.com/v2/project/{id}/versions?game_versions=["<mc-version>"]&loaders=["paper","spigot","bukkit"]
```

Use the most recent version from the response.

### 3. CurseForge

If not found on Modrinth, search CurseForge via `/v1/mods/search`. Retrieve the latest file supporting the target MC version and Paper/Spigot/Bukkit.

### 4. GitHub / GitLab releases

If not found on CurseForge, search GitHub/GitLab for `<plugin-name> minecraft paper` and inspect releases for a JAR matching the target MC version.

### 5. Not found anywhere

Flag as `NOT_FOUND`. Notes column: `Check Discord for <plugin-name>`.

---

## Compatibility heuristic

| Situation | Flag |
|-----------|------|
| Exact MC version match in API | Confirmed compatible |
| Same minor series (e.g. `1.21.10` for target `1.21.11`) | Likely compatible — add note |
| Open GitHub issues (last 90 days) with target version + `crash`/`broken`/`incompatible` | Add issue URL to Notes |

---

## Status definitions

| Status | Meaning |
|--------|---------|
| `UP_TO_DATE` | Latest available version matches current installed version |
| `UPDATE_AVAILABLE` | A newer version exists for the target MC version |
| `INCOMPATIBLE` | Plugin exists but has no build for the target MC version |
| `ABANDONED` | No update in 12+ months AND no build for any newer MC version |
| `NOT_FOUND` | Could not locate the plugin on any source |

---

## Report format

Return EXACTLY this format:

```
## Plugin Report: {plugin-name}

- **Status:** {UP_TO_DATE | UPDATE_AVAILABLE | INCOMPATIBLE | ABANDONED | NOT_FOUND}
- **Installed version:** {version from JAR filename}
- **Latest version:** {version} — [{source}]({url})
- **Version bump:** {e.g. "2.4.5-b → 2.5.0" or "UP_TO_DATE"}
- **Source:** {Hangar | Modrinth | CurseForge | GitHub | GitLab | Not found}
- **Source URL:** {direct link to plugin page or releases page — used by changelog agent}
- **MC version match:** {Exact | Same minor series (flag) | No build found}
- **Open issues (last 90 days):** {None | [title](url)}
- **Notes:** {any extra context, e.g. "dev confirmed no 1.21.11 path" or "edge build — stable now available"}
```
