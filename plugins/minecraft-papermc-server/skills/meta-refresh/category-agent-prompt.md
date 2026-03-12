# Category Agent Prompt Template

Use this file to construct each category agent's prompt. Replace `{placeholders}` with actual values before dispatching.

---

## Prompt to inject

Every category agent prompt MUST start with:

> Read the file `{resolved-path-to}/compat-check/SKILL.md` and follow its procedure for every plugin you assess and every gap candidate you recommend.

**Path resolution:** Replace `{resolved-path-to}` with the absolute path to `../compat-check/SKILL.md` resolved from this skill's base directory.

Then inject:

---

You are auditing the **{category}** category for a PaperMC server plugin meta-refresh.

**Your plugins in this category:**
{plugin list — filenames + inferred versions}

**Target MC version:** {mc-version}
**Platform:** Paper (compatible with Spigot/Bukkit API)
**Installed plugin list (all categories):** {full list — for dependency checking}

---

## Research steps

**Step 1 — Fetch top 10 plugins for this category on Hangar:**
```
GET https://hangar.papermc.io/api/v1/projects?q={category-keyword}&platform=PAPER&platformVersion={mc-version}&limit=10&sort=-downloads
```
If the category keyword returns 0 results, try a broader keyword (e.g., `admin`, `utility`, `management`).

**Step 2 — Fetch top 10 plugins for this category on Modrinth:**
```
GET https://api.modrinth.com/v2/search?query={keyword}&facets=[["project_type:mod","project_type:plugin"],["server_side:required","server_side:optional"],["versions:{mc-version}"],["categories:paper","categories:spigot","categories:bukkit"]]&index=downloads&limit=10
```
Note: Modrinth uses both `project_type:mod` (for some server-side projects) and `project_type:plugin` — search both via the OR facet above.

**Step 3 — For each installed plugin in this category, fetch stats and run compat check:**
```
GET https://hangar.papermc.io/api/v1/projects/{author}/{slug}
```
or search Modrinth if not on Hangar:
```
GET https://api.modrinth.com/v2/search?query={plugin-name}&facets=[["versions:{mc-version}"],["project_type:mod","project_type:plugin"]]
```
Get: download count, last updated date, project slug. Then run the Plugin Compatibility Check (from compat-check skill) for each plugin.

**Step 4 — Dependency check before any REMOVE verdict:**

Before assigning `REMOVE` to any plugin, inspect the `plugin.yml` (or `paper-plugin.yml`) `depend:` fields of every other installed plugin. If any other plugin hard-depends on the removal target, do NOT assign `REMOVE` — assign `INVESTIGATE` and flag the conflict explicitly.

**Step 5 — Detect redundancy:** Multiple plugins in this category doing the same thing. Flag any pair where feature overlap is substantial.

**Step 6 — Detect gaps:** Top-10 plugins from Hangar or Modrinth not in the installed list that suit the allowed profile. Run the Plugin Compatibility Check for every gap candidate before recommending ADD. Drop any candidate with `✗ none`. Check all required dependencies too.

**Allowed plugin categories — only recommend these:**
- Performance (TPS optimization, async processing, caching)
- Admin tooling (console utilities, monitoring, debugging)
- Permissions management
- World management (multiworld, void world, border management)
- Maps and dynmap-style visualization
- QoL for operators (tab completion, command aliases, scheduling)
- Cosmetic (particle effects, chat formatting that doesn't change gameplay)

**Vanilla+ exclusions — never recommend these:**
- Economy plugins (Vault, EssentialsX economy, shop plugins)
- Minigame frameworks (MiniGames, Minigame-related plugins)
- Custom enchantment plugins (EcoEnchants, Enchantment+ etc.)
- Gameplay-altering plugins (custom crafting, new mobs, new dimensions)
- Grief-prevention plugins that add new gameplay mechanics (land claiming with economic costs, etc.)

**Step 7 — Surface wildcards:** After completing gap detection, identify 1-2 interesting plugins that fall outside the vanilla+ profile above but could have legitimate utility on a vanilla+ server. Label them clearly as outside-profile. Examples: CoreProtect (block logging/rollback — useful for grief recovery), BlueMap (3D web map — heavier but more feature-rich than dynmap).

**Step 8 — Assign verdict per plugin:**

| Signal | Verdict |
|--------|---------|
| Top-3 by downloads for category, compat ✓, fits allowed profile | `KEEP` |
| Alternative has 2x+ downloads, compat ✓, covers same function | `REPLACE(<alt>)` |
| Two plugins cover identical function | `REDUNDANT(with <x>)` |
| Top-10 plugin not in list, compat ✓, deps ✓, suits allowed profile | `ADD` |
| Removal target has a hard dependent — cannot safely remove | `INVESTIGATE` |
| Data insufficient or signals conflict | `INVESTIGATE` |
| Plugin has `✗ none` compat | `INCOMPATIBLE` |

---

## Output format

Return a Category Report in EXACTLY this format:

```
## Category Report: {category-name}

### Assessed plugins
| Plugin | Downloads | Last Updated | Compat | Verdict | Alternative | Pros | Cons |
|--------|-----------|--------------|--------|---------|-------------|------|------|
| LuckPerms | 12M | 2026-01 | ✓ exact | KEEP | — | best-in-class permissions | — |
| OldPlugin | 40k | 2023-06 | ✗ none | INCOMPATIBLE | [ModernAlt](url) | 2M DL, 1.21 ✓ | — |

### Gap recommendations
| Plugin | Downloads | Last Updated | Compat | Deps OK? | Reason to add | Link |
|--------|-----------|--------------|--------|----------|---------------|------|
| Spark | 8M | 2026-02 | ✓ exact | Yes | profiling + TPS diagnostics | [link](url) |

### Wildcards (outside vanilla+ profile)
| Plugin | Downloads | Why it's interesting | Link |
|--------|-----------|----------------------|------|
| CoreProtect | 3M | Block logging + rollback — useful for grief recovery even on vanilla+ servers | [link](url) |

### Redundancies detected
| Plugin A | Plugin B | Overlap | Recommendation |
|----------|----------|---------|----------------|

### Raw signals used
- Hangar top-10 for {category} + {mc-version} (by downloads): [list names]
- Modrinth top-10 for {category} + {mc-version} (by downloads): [list names]
- Compatibility verified via compat-check for all plugins and candidates
```
