---
name: meta-refresh
description: Use when the user wants to know if their PaperMC server plugins are still optimal, when plugins may have been superseded by better alternatives, when redundant plugins are suspected, or when gaps in plugin coverage exist for a given MC version and server profile.
---

REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents
REQUIRED SUB-SKILL: compat-check

# PaperMC Server Plugins Meta Refresh

Audit a PaperMC server's installed plugins to determine whether each is still best-in-class, find better alternatives using live Hangar and Modrinth data, record approved decisions to a shared decision doc, then chain to version-refresh.

## Inputs

Ask for any of these not already provided:

- **Server SSH alias** — e.g. `minecraft`. Used for all remote reads (`ssh <alias> "..."`)
- **Server files path** — absolute path on the remote host where the server lives, e.g. `/opt/minecraft/server`. Contains the `plugins/` subdirectory.
- **Target MC version** — e.g. `1.21.4`
- **Server profile** — default: vanilla+ PaperMC (performance, admin tooling, world management, operator QoL). Explicitly excluded: economy, minigames, custom enchantments, gameplay-altering plugins, any plugin that reveals non-vanilla information to players.
- **Decision doc path** — if passed from audit, use it. Otherwise: `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` (create if not exists)

---

## Read-only phases

No files are written in this section.

### Phase 1 — Discover and Categorize

Fetch installed plugins from the remote server:
```bash
ssh <alias> "ls {server-files-path}/plugins/*.jar"
```

For each JAR, infer the plugin name and version. Try in order:
1. Parse from filename — most plugins use `PluginName-X.Y.Z.jar` convention
2. If version is unclear, extract from `plugin.yml` inside the JAR:
   ```bash
   ssh <alias> "unzip -p {server-files-path}/plugins/<name>.jar plugin.yml 2>/dev/null | grep '^version:'"
   ```

Assign each plugin to exactly one category:

| Category | Example plugins |
|----------|----------------|
| `performance` | Spark, Paper (built-in), Chunky, ClearLag |
| `auth-security` | AuthMe, SkinsRestorer, nLogin |
| `maps-visualization` | DynMap, BlueMap, Pl3xMap |
| `world-management` | Multiverse-Core, WorldBorder, VoidGen |
| `admin-tools` | LuckPerms, EssentialsX (admin subset), LSQL, TAB |
| `qol-cosmetic` | Maintenance, ServerUtils, chat formatting plugins |
| `library` | Vault, PlaceholderAPI, ProtocolLib, PacketEvents |

Output: category → [plugin list with inferred versions] map.

### Phase 2 — Parallel Category Agents

**REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents** — use it to dispatch and manage all category agents.

Run one `server-category-agent` per non-library category. Dispatch all with `run_in_background: true`.

Read `./category-agent-prompt.md` (in this skill's directory) for the full agent prompt template. Inject per-agent values (category name, plugin list with inferred versions, MC version, full installed plugin list for dependency checking) from Phase 1.

When constructing sub-agent prompts, resolve all relative paths (like `../compat-check/SKILL.md`) to absolute paths using this skill's base directory before injecting.

Wait for all agents to complete before Phase 3.

### Phase 3 — Synthesize

- Merge all Category Reports into one list.
- Resolve conflicts (same plugin recommended by two agents — use the one with more supporting data).
- De-duplicate gap candidates.

### Phase 4 — Upgrade Plan

Build the numbered upgrade plan from all category reports. Read `./upgrade-plan-format.md` (in this skill's directory) for the exact output format and table rules.

After presenting the plan, tell the user:

> Reply with:
> - **"approve all"** — apply every proposed change
> - **"approve 1,3"** — apply only items #1 and #3
> - **"skip 2"** — approve all except #2
> - **"approve W1"** — promote wildcard W1 to a full ADD entry
> - **"cancel"** — abort, no changes made

**No files are written until the user explicitly responds.**

---

## Write phases

Files are written only after the user responds to the upgrade plan.

### Phase 5 — Write Decision Doc

**Decision doc path:** `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`

Create `./minecraft-audits/` if it doesn't exist. Create the file if it doesn't exist. If it already exists (created by audit), append to it.

**Header (write at top if creating):**

```md
# PaperMC Server Audit — YYYY-MM-DD
Server: <server-name>
MC Version: <version>
Platform: Paper
```

**Meta decisions section (always append):**

```md
## Meta decisions
| # | Action | Plugin | Alternative | Decision |
|---|--------|--------|-------------|----------|
| 1 | ADD | Spark | — | approved |
| 2 | REPLACE | EssentialsX | CMI | skipped |
| 3 | REMOVE | OldPlugin | — | approved |
```

Use `approved`, `skipped`, or `cancelled` in the Decision column.

### Phase 6 — Chain to Version-Refresh

After writing the decision doc, say:

> Meta audit complete. Decision doc saved to `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`.
>
> Proceed to version-refresh? **(yes / cancel)**

- **If yes:** Say "Invoking `version-refresh`." and invoke it, passing the decision doc path and server connection details.
- **If cancel:** Ask: "Delete the decision doc to keep tidy, or save it for a future run? **(delete / keep)**" — act on response.

---

## Failure Handling

If any phase produces unexpected results — malformed agent output, Hangar or Modrinth API errors, agents returning empty or garbled Category Reports — invoke `superpowers:systematic-debugging` before retrying or escalating to the user.

---

## Common Mistakes

- **Recommending plugins without running compat-check** — every plugin verdict and every gap candidate MUST have a verified compat status. This is the #1 failure mode.
- **Trusting Modrinth search facets as proof of exact-version builds** — the `versions:X` facet uses minor-series matching, not exact matching. Always call the `/version` endpoint to confirm.
- **Writing files before user approval** — Phases 1-4 are strictly read-only. No decision doc writes until the user responds to the upgrade plan.
- **Recommending plugins that violate vanilla+ server profile** — never recommend economy, minigames, custom enchantments, or plugins that alter gameplay beyond vanilla+.
- **Missing dependency checks before REMOVE** — always inspect `plugin.yml` `depend:` fields of other installed plugins before assigning REMOVE. Hard dependents block removal.

---

## Meta Signal Sources (priority order)

1. Hangar download count + prominence for target MC version — primary signal
2. Modrinth download count + `date_modified` — secondary signal
3. GitHub stars + last push date — tiebreaker for close calls
