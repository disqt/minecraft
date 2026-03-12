---
name: version-refresh
description: Use when the user wants to check their PaperMC server plugins for version updates, find newer builds across Hangar / Modrinth / CurseForge / GitHub, and optionally apply approved updates via staging verification.
---

REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents
REQUIRED SUB-SKILL: compat-check

# PaperMC Server Plugins Version Refresh

Check every plugin on a PaperMC server for version updates, present a numbered upgrade plan, record approved decisions to the decision doc, then chain to the executor for staging verification and production apply.

## Inputs

Ask for any of these not already provided:

- **Production SSH alias** — e.g. `minecraft`. Used for all remote reads.
- **Server files path** — absolute path on the remote host, e.g. `/home/minecraft/serverfiles`. Contains the `plugins/` subdirectory.
- **Target MC version** — e.g. `1.21.4`. Auto-detect from `{server-files-path}/version_history.json` if not provided.
- **Decision doc path** — if passed from meta-refresh, use it. Otherwise: `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` (create if not exists).

---

## Read-only phases

No files are written in this section.

### Step 1 — Read the plugins folder

Fetch the plugin list from the remote server:

```bash
ssh <alias> "ls {server-files-path}/plugins/*.jar"
```

For each JAR, extract plugin name and current version. Try in order:

1. Parse from filename — most plugins use `PluginName-X.Y.Z.jar` convention.
2. If version is unclear, extract from `plugin.yml` inside the JAR:
   ```bash
   ssh <alias> "unzip -p {server-files-path}/plugins/<name>.jar plugin.yml 2>/dev/null | grep '^version:'"
   ```

Track the full list: name, inferred version, and source filename.

### Step 2 — Dispatch one agent per plugin (parallel, background)

**REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents** — use it to dispatch and manage all version agents.

Dispatch all agents with `run_in_background: true`. Wait for all to complete before Step 3.

Read `./version-agent-prompt.md` (in this skill's directory) for the lookup procedure, compatibility heuristic, status definitions, and report format each agent must follow.

Pass each agent: plugin name, installed version, target MC version.

### Step 2.5 — Dispatch changelog agents (parallel, background)

For every plugin with `UPDATE_AVAILABLE` status from Step 2, dispatch one changelog agent with `run_in_background: true`. Pass each agent:

- Plugin name, installed version, latest version
- Source and Source URL from the version agent's report (no re-searching)

Read `./changelog-agent-prompt.md` (in this skill's directory) for the agent prompt template.

Wait for all changelog agents to complete before Step 3.

Accumulate all changelog results into a changelog digest — this will be passed to the executor in Step 6.

### Step 3 — Build upgrade plan

Consolidate all Plugin Reports and Changelog results into a numbered upgrade plan. Only include plugins with actionable status (`UPDATE_AVAILABLE`, `INCOMPATIBLE`, `ABANDONED`, `NOT_FOUND`). `UP_TO_DATE` plugins are listed collapsed at the bottom.

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

**Decision doc path:** use path passed from meta-refresh or audit, or `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`.

Create `./minecraft-audits/` if it doesn't exist. Create the file if it doesn't exist. If it already exists, append:

```md
## Version decisions
| # | Action | Plugin | Old | New | Decision |
|---|--------|--------|-----|-----|----------|
| 1 | UPDATE | EssentialsX | 2.20.0 | 2.21.0 | approved |
| 2 | FLAG | WorldEdit | 7.3.1 | — | skipped |
```

Use `approved`, `skipped`, or `cancelled` in the Decision column.

### Step 6 — Chain to executor

After writing the decision doc, say:

> Version audit complete. Decision doc updated at `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`.
>
> Proceed to executor to stage, verify, and apply all approved changes? **(yes / cancel)**

- **If cancel:** Ask: "Delete the decision doc to keep tidy, or save it for a future run? **(delete / keep)**" — act on response.
- **If yes:** Say "Invoking `executor`." and invoke it as a foreground skill (not a background agent).

Invoke `executor`, passing:
- Decision doc path
- Production SSH alias
- Server files path
- Target MC version
- Staging SSH alias (from inputs, or ask now if not yet provided)
- Staging files path (from inputs, or ask now if not yet provided)
- Staging boot command (from inputs, or ask now if not yet provided)
- Staging Java path (from inputs, or ask now if not yet provided)
- Changelog digest (accumulated from Step 2.5)

---

## Failure Handling

If any step produces unexpected results — version agents returning malformed reports, API response format changes, SSH commands failing, changelog agents failing to parse releases — invoke `superpowers:systematic-debugging` before retrying or escalating to the user.

---

## Common Mistakes

- **Guessing version numbers** — always use actual API responses. Never fabricate or infer version strings.
- **Writing decision doc before user approval** — Steps 1-4 are strictly read-only. No writes until the user responds.
- **Dispatching executor before user confirms** — always ask "yes / cancel" before invoking the executor.
- **Using a background agent for the executor** — the server executor runs foreground (not `run_in_background: true`), because it requires interactive confirmation during staging verification.
- **Forgetting the changelog digest** — accumulate all changelog results in Step 2.5 and pass them to the executor. The executor needs this to build the deployment summary.
