---
name: meta-refresh
description: Use when the user wants to know if their Prism Launcher Fabric modset is still optimal, when mods may have been superseded by better alternatives, when the user suspects redundant mods, or when gaps in coverage are suspected for a given MC version and player profile.
---

REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents
REQUIRED SUB-SKILL: compat-check

# Minecraft Prism Mods Meta Refresh

Audit a Prism Launcher Fabric instance to determine whether each mod is still best-in-class, find better alternatives using live Modrinth data, record approved decisions to a shared decision doc, then chain to version-refresh.

## Inputs

Ask for any of these not already provided:

- **Prism instance name** — auto-detect by listing `{PRISM_INSTANCES}`
- **Target MC version** — e.g. `1.21.11`
- **Modloader** — default: `Fabric`
- **Player profile** — default: vanilla+ Fabric client (performance, subtlety, no gameplay changes). Explicitly excluded: minimap/world map mods, block/entity info overlays (Jade, WAILA, etc.), persistent HUD overlays if BetterF3 or equivalent is already present, any mod that reveals world information not accessible in vanilla.
- **Reference packs** — default: DisruptiveBuilds REFINED (`dbs-minecraft-refined`) and PLUS (`dbs-minecraft-plus`) on Modrinth
- **Server SSH host** *(optional)* — e.g. `minecraft`. If provided, check server plugins via `ssh <host> "ls {SERVER_PLUGINS_DIR}"` to determine which server-side companions are active (DHSupport enables DH LOD sync; Lithium and Krypton are primarily server-side — client-only installs have partial benefit).
- **Decision doc path** — if passed from audit, use it. Otherwise: `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md` (create if not exists)

---

## Read-only phases

No files are written in this section.

### Phase 1 — Categorize

If a server host was provided, fetch active plugins:
```bash
ssh <host> "ls {SERVER_PLUGINS_DIR}"
```
Note server-side companions — affects verdicts for client mods with server-side counterparts (e.g. DHSupport enables DH LOD sync, Lithium/Krypton have server-side performance components).

Read `<instance>/.minecraft/mods/` (include `.disabled` files). Assign each mod to exactly one category:

| Category | Example mods |
|----------|-------------|
| `performance` | sodium, ferritecore, entityculling, dynamic-fps, noisium |
| `rendering` | iris, continuity, entity_texture_features, entity_model_features |
| `audio` | sound-physics-remastered, sounds |
| `hud-ui` | appleskin, BetterF3, durabilitytooltip, modmenu, lighty |
| `qol` | MouseTweaks, smoothscroll, AutoWalk, camerautils, PickUpNotifier |
| `shaders` | shader packs, EuphoriaPatcher |
| `library` | fabric-api, cloth-config, yet-another-config-lib, etc. |
| `disabled` | any `.disabled` mod — track separately, note why disabled if inferable |

Output: category → [mod list] map.

### Phase 2 — Parallel Category Agents

**REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents** — use it to dispatch and manage all category agents.

Run one general-purpose agent per non-library, non-disabled category. Dispatch all with `run_in_background: true`.

Read `./category-agent-prompt.md` (in this skill's directory) for the full agent prompt template. Inject per-agent values (category name, user mods, MC version, modloader, server-side companions) from Phase 1.

When constructing sub-agent prompts, resolve all relative paths (like `../compat-check/SKILL.md`) to absolute paths using this skill's base directory before injecting.

Wait for all agents to complete before Phase 3.

### Phase 3 — Synthesize

- Merge all Category Reports into one list.
- Resolve conflicts (same mod recommended by two agents — use the one with more supporting data).
- De-duplicate gap candidates.

### Phase 4 — Upgrade Plan

Build the numbered upgrade plan from all category reports. Read `./upgrade-plan-format.md` (in this skill's directory) for the exact output format and table rules.

After presenting the plan, tell the user:

> Reply with:
> - **"approve all"** — apply every proposed change
> - **"approve 1,3"** — apply only items #1 and #3
> - **"skip 2"** — approve all except #2
> - **"cancel"** — abort, no changes made

**No files are written until the user explicitly responds.**

---

## Write phases

Files are written only after the user responds to the upgrade plan.

### Phase 5 — Write Decision Doc

**Decision doc path:** `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`

Create `./minecraft-audits/` if it doesn't exist. Create the file if it doesn't exist. If it already exists (created by audit), append to it.

**Header (write at top if creating):**

```md
# Minecraft Audit — YYYY-MM-DD
Instance: <name>
MC Version: <version>
Modloader: <loader>
```

**Meta decisions section (always append):**

```md
## Meta decisions
| # | Action | Mod | Alternative | Decision |
|---|--------|-----|-------------|----------|
| 1 | ADD | Lithium | — | approved |
| 2 | REPLACE | flow | Smooth Gui | skipped |
| 3 | REMOVE | noisium | — | approved |
```

Use `approved`, `skipped`, or `cancelled` in the Decision column.

### Phase 6 — Chain to Version-Refresh

After writing the decision doc, say:

> Meta audit complete. Decision doc saved to `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`.
>
> 1. **Proceed** — continue to version-refresh
> 2. **Cancel** — stop here

- **If 1:** Say "Invoking `version-refresh`." and invoke it, passing the decision doc path and instance name.
- **If 2:** Ask: "1. **Delete decision doc** — keep tidy, or 2. **Keep decision doc** — save for a future run?" — act on response.

---

## Failure Handling

If any phase produces unexpected results — malformed agent output, Modrinth API errors, agents returning empty or garbled Category Reports — invoke `superpowers:systematic-debugging` before retrying or escalating to the user.

---

## Common Mistakes

- **Recommending mods without running compat-check** — every mod verdict and every gap candidate MUST have a verified compat status. This is the #1 failure mode.
- **Trusting Modrinth search facets as proof of exact-version builds** — the `versions:X` facet uses minor-series matching, not exact matching. Always call the `/version` endpoint to confirm.
- **Writing files before user approval** — Phases 1-4 are strictly read-only. No decision doc writes until the user responds to the upgrade plan.
- **Recommending mods that violate vanilla+ profile** — never recommend minimap, world map, block/entity info overlays, or mods that reveal non-vanilla information.

---

## Meta Signal Sources (priority order)

1. Modrinth download count + `date_modified` for target MC version — primary signal
2. Presence in DisruptiveBuilds REFINED or PLUS pack — validation signal
3. GitHub stars + last push date — tiebreaker for close calls
