---
name: version-refresh
description: Use when the user wants to check their Prism Launcher Fabric (or NeoForge) modpack for mod version updates, find newer JAR files across Modrinth / CurseForge / GitHub, and optionally install approved updates into a cloned instance.
---

REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents

# Minecraft Prism Mods Version Refresh

Check every mod in a Prism Launcher instance for version updates, present a numbered upgrade plan, record approved decisions to the decision doc, then dispatch a background executor that clones the instance and applies all approved meta and version changes.

## Inputs

Ask for any of these not already provided:

- **Prism instance name** — default: auto-detect by listing `{PRISM_INSTANCES}` and asking the user to pick one.
- **Target MC version** — e.g. `1.21.11`. Required; ask explicitly if missing.
- **Modloader** — Fabric or NeoForge. Infer from `mmc-pack.json` inside the instance if possible; otherwise ask.
- **Decision doc path** — if passed from meta-refresh, use it. Otherwise: `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md` (create if not exists).

---

## Read-only phases

No files are written in this section.

### Step 1 — Read the mods folder

Scan: `{PRISM_INSTANCES}/<instance-name>/.minecraft/mods/`

- List every `.jar` and `.jar.disabled` file.
- Extract mod name and current version from filename (best-effort; filenames are often `modname-mcversion-modversion.jar`).
- Track which files are `.disabled`.

### Step 2 — Dispatch one agent per mod (parallel, background)

**REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents** — use it to dispatch and manage all version agents.

Dispatch all agents with `run_in_background: true`. Wait for all to complete before Step 3.

Read `./version-agent-prompt.md` (in this skill's directory) for the lookup procedure, compat heuristic, status definitions, and report format each agent must follow.

### Step 2.5 — Dispatch changelog agents (parallel, background)

For every mod with `UPDATE_AVAILABLE` status from Step 2, dispatch one changelog agent with `run_in_background: true`. Pass each agent:
- Mod name, installed version, latest version
- Source and Source URL from the version agent's report (no re-searching)

Read `./changelog-agent-prompt.md` (in this skill's directory) for the agent prompt template.

Wait for all changelog agents to complete before Step 3.

### Step 3 — Build upgrade plan

Consolidate all Mod Reports and Changelog results into a numbered upgrade plan. Only include mods with actionable status (UPDATE_AVAILABLE, INCOMPATIBLE, ABANDONED, NOT_FOUND). UP_TO_DATE mods are listed collapsed at the bottom.

Read `./version-upgrade-plan-format.md` (in this skill's directory) for the exact format.

### Step 4 — Present and wait for approval

Present the upgrade plan. Tell the user:

> Reply with:
> - **"approve all"** — apply every proposed change
> - **"approve 1,3"** — apply only items #1 and #3
> - **"skip 2"** — approve all except #2
> - **"cancel"** — abort, no changes made

**No files are written until the user explicitly responds.**

---

## Write phases

Files are written only after the user responds.

### Step 5 — Write version decisions to decision doc

**Decision doc path:** use path passed from meta-refresh, or `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`.

Create `./minecraft-audits/` if it doesn't exist. Create the file if it doesn't exist. If it already exists, append:

```md
## Version decisions
| # | Action | Mod | Old | New | Decision |
|---|--------|-----|-----|-----|----------|
| 1 | UPDATE | sounds | 2.4.23+edge | 2.4.23+fabric | approved |
| 2 | FLAG | flow | 2.2.0 | — | skipped |
```

Use `approved`, `skipped`, or `cancelled` in the Decision column.

### Step 6 — Dispatch background executor

After writing the decision doc, say:

> Version audit complete. Decision doc updated at `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`.
>
> Dispatch background executor to apply all approved changes? **(yes / cancel)**

- **If cancel:** Ask: "Delete the decision doc to keep tidy, or save it for a future run? **(delete / keep)**" — act on response.
- **If yes:** Say "Dispatching executor." and dispatch a background agent with `run_in_background: true`.

Read `./executor-agent-spec.md` (in this skill's directory) for the full executor spec. Pass the executor: decision doc path, instance name, MC version, modloader.

---

## Failure Handling

If any step produces unexpected results — version agents returning malformed reports, API response format changes, changelog agents failing to parse releases — invoke `superpowers:systematic-debugging` before retrying or escalating to the user.

---

## Common Mistakes

- **Guessing version numbers** — always use actual API responses. Never fabricate or infer version strings.
- **Writing decision doc before user approval** — Steps 1-4 are strictly read-only. No writes until the user responds.
- **Dispatching executor before user confirms** — always ask "yes / cancel" before launching the background executor.
