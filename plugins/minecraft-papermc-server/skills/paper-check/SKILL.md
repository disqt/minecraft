---
name: paper-check
description: Use when the user wants to check if a PaperMC server can be upgraded to a newer version, and which plugins would break or need updates.
---

REQUIRED SUB-SKILL: compat-check

# PaperMC Version Check

Check whether a newer PaperMC version is available and verify all installed plugins have compatible builds for it. Produces a Paper Compatibility Report.

## Inputs

Ask for any of these not already provided:

- **Production SSH alias**
- **Server files path**
- **Decision doc path** — if passed from audit, use it. Otherwise: `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`

---

## Read-only phases

No files are written in this section.

### Phase 1 — Read current state

SSH into production:
- Read `{server-files-path}/version_history.json` — extract current MC version and Paper build number
- List `{server-files-path}/plugins/*.jar` — build installed plugin list
- For each plugin JAR, extract version from filename or from `plugin.yml` inside the JAR:
  `ssh <alias> "cd {server-files-path} && jar -xf plugins/<plugin>.jar plugin.yml && grep '^version:' plugin.yml && rm plugin.yml"`

### Phase 2 — Query PaperMC API

GET https://api.papermc.io/v2/projects/paper/versions/

Compare against current version.

- If no newer version: report "Paper is up to date at {version}", write `## Paper decisions: no update available` to decision doc, offer to skip to meta-refresh
- If one newer version: proceed to Phase 3 with that version as target
- If multiple newer versions: present the list to the user, let them pick, then proceed

### Phase 3 — Compatibility check

For the selected target version:

1. Fetch Paper changelog: `GET https://api.papermc.io/v2/projects/paper/versions/{target}/builds` — read commit messages from builds between current and target
2. Run compat-check (read `../compat-check/SKILL.md`) against every installed plugin for the target MC version
3. Flag any plugin with `✗ none` as BLOCKER

### Phase 4 — Produce Paper Compatibility Report

Read `./paper-compat-report-format.md` for exact output format.

Present to user. Then:

- If ALL CLEAR: "All {N} plugins have builds for {target}. Approve {target} as the target version? Remaining phases will use it."
- If BLOCKERs: "{N} plugins block the upgrade: {list}. Stay on current version ({current}) and proceed to meta-refresh?"

---

## Write phases

Files are written only after the user responds to the compatibility report.

### Phase 5 — Write Paper decisions

Append to decision doc:

```md
## Paper decisions
| Decision | Value |
|----------|-------|
| Target version | {target} or {current} (staying) |
| Reason | ALL CLEAR / {N} blockers |
| Blockers | {list or none} |
```

### Phase 6 — Chain to meta-refresh

After writing the decision doc, say:

> Paper check complete. Decision doc updated.
>
> Proceed to meta-refresh? **(yes / cancel)**

- **If yes:** invoke meta-refresh, passing decision doc path, target MC version, and all SSH/path inputs.
- **If cancel:** Ask: "Delete the decision doc to keep tidy, or save it for a future run? **(delete / keep)**" — act on response.

---

## Failure Handling

If PaperMC API is unreachable or returns unexpected responses, invoke `superpowers:systematic-debugging`.

---

## Common Mistakes

- **Assuming version_history.json format** — always parse, don't assume structure. It's a JSON array of version entries.
- **Comparing version strings lexically** — MC versions like 1.21.11 vs 1.21.2 need semantic comparison (1.21.11 > 1.21.2)
- **Skipping compat-check for "obviously compatible" plugins** — run it on every plugin, no exceptions
- **Not extracting plugin versions** — needed for the report. Use `plugin.yml` inside JARs when filename doesn't contain version info
