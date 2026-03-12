---
name: compat-check
description: Use when verifying whether a PaperMC server plugin has a build for a specific MC version before recommending KEEP, ADD, REPLACE, or REMOVE for that plugin.
---

# PaperMC Plugin Compatibility Check

Verify a plugin has an actual build for the target MC version before including it in any verdict or recommendation. Run this for EVERY plugin assessed and EVERY gap candidate — never skip.

## Procedure

For each plugin, call Hangar first:

```
GET https://hangar.papermc.io/api/v1/projects/{slug}/versions?platform=PAPER&platformVersion={mc-version}
```

If the slug is unknown, find it first:
```
GET https://hangar.papermc.io/api/v1/projects?query={plugin-name}&limit=5
```
Take the top result's `slug`.

If not found on Hangar, fall back to Modrinth:

```
GET https://api.modrinth.com/v2/project/{slug}/version?game_versions=["{mc-version}"]&loaders=["paper","spigot","bukkit"]
```

Paper implements the Spigot/Bukkit API — any hit on paper, spigot, or bukkit counts as compatible.

If the slug is unknown on Modrinth, find it first:
```
GET https://api.modrinth.com/v2/search?query={plugin-name}&facets=[["project_type:plugin"]]
```
Take the top result's `slug`.

### Read the response

| Result | Status | Action |
|--------|--------|--------|
| Hangar: versions returned, platformVersion matches exactly | `✓ exact` | Use latest version + date |
| Hangar: no results → Modrinth returns results, game version matches exactly | `✓ exact` | Use latest version + date, note source as Modrinth |
| No Hangar results → Modrinth no results → retry Modrinth with minor series (e.g. `1.21.1` for target `1.21.11`) → found | `~ minor` | Flag as unconfirmed |
| Nothing on Hangar or Modrinth → check CurseForge / GitHub | `? external` | Note source |
| Nothing found anywhere | `✗ none` | Block — see rules |

## Check dependencies

### ADD candidates: recursive dependency check

For every ADD candidate, read its `plugin.yml` `depend:` field (hard dependencies) and `softdepend:` field (soft dependencies). For each hard dependency not already installed on the server, run this same compat-check procedure on it. If any hard dependency has `✗ none`, the candidate cannot be recommended.

Soft dependencies (softdepend) do not block a recommendation but should be noted in the report if they are missing.

### REMOVE candidates: reverse dependency check

Before recommending REMOVE for any plugin, check that no other installed plugin has the removal target listed in its `depend:` field. A plugin with a hard `depend:` on the removal target will break if the target is removed. If a reverse hard dependency exists, either mark the removal as blocked or include the dependent plugin in the same REMOVE decision.

## Rules

- **`✗ none`** → NEVER recommend KEEP, ADD, or REPLACE with this plugin. Flag as `INCOMPATIBLE` (installed plugin) or drop from gap list (candidate).
- **`~ minor`** → May include, but flag in report as "unconfirmed for exact version".
- **`? external`** → Include with source noted.
- **Missing hard dep with `✗ none`** → Drop the candidate entirely; note why.
- **Reverse hard dep blocks REMOVE** → Block removal or include the dependent plugin in the same removal decision; note why.

## Report column

Add to every row in the Plugin Report:

```
| Compat | Latest for target | Date |
| ✓ exact | 2.11.0 | 2026-02 |
| ~ minor | 2.10.3 | 2025-11 |
| ✗ none | — | — |
```

## Baseline failure (why this skill exists)

Hangar search results and Modrinth search results do not guarantee that an exact-version build exists. A plugin can appear in Hangar search results for a given platformVersion via minor-series matching — the search index may include it under `1.21` when only a `1.21.1` JAR was ever published. The Modrinth `versions:X` search facet has the same behavior. This skill closes that gap by calling the versions endpoint directly and confirming that a downloadable artifact for the exact target MC version exists before any verdict is issued.
