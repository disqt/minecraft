---
name: papermc-audit
description: Use when the user wants to do a full refresh of their PaperMC server plugins in one session — check for Paper updates, audit plugin quality, update plugin versions, stage-test and apply changes safely.
---

REQUIRED SUB-SKILL: paper-check
REQUIRED SUB-SKILL: meta-refresh
REQUIRED SUB-SKILL: version-refresh

# PaperMC Server Audit

Entry point for a full server plugin refresh. Creates the shared decision doc, then invokes paper-check. The skills chain automatically: paper-check → meta-refresh → version-refresh → executor.

## Inputs

Ask for any of these not already provided:

- **Production SSH alias** — SSH alias for the live server (e.g. `minecraft`)
- **Server files path** — path to `serverfiles/` on production. Auto-detect: `ssh <alias> "ls /home/*/serverfiles/paper.jar 2>/dev/null || ls /home/*/serverfiles/server.jar 2>/dev/null"` and infer from result
- **LGSM script path** — path to LGSM entry point. Auto-detect: `ssh <alias> "ls /home/*/pmcserver 2>/dev/null || ls /home/*mcserver 2>/dev/null"`
- **Staging SSH alias** — SSH alias for the staging/test server
- **Staging files path** — path to server files on staging host
- **Staging boot command** — command to start PaperMC on staging (e.g. `java -jar paper.jar nogui`). Staging may not use LGSM
- **Staging Java path** — Java binary on staging (e.g. `java` or a full SDKMAN path)
- **Target MC version** — auto-detect from production `version_history.json`, or ask

---

## Flow

```
papermc-audit
  └─ gathers inputs, auto-detects server state
  └─ creates decision doc
  └─ invokes paper-check                          ← Phase 1
       └─ checks Paper build currency, flags update if needed
       └─ writes Paper decisions to decision doc
       └─ invokes meta-refresh                    ← Phase 2
            └─ categorizes plugins, dispatches parallel category agents
            └─ upgrade plan → user approves → writes meta decisions to doc
            └─ invokes version-refresh            ← Phase 3
                 └─ checks each plugin for updates
                 └─ upgrade plan → user approves → appends version decisions to doc
                 └─ dispatches executor           ← Phase 4
                      └─ stage on test server → verify → apply to production
```

Decision doc (`./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`) is the shared contract between all phases.

---

## Step 1 — Auto-detect server state

SSH into production:

- Read `{server-files-path}/version_history.json` for current Paper version and MC version
- List `{server-files-path}/plugins/` for plugin count
- Report: "Found Paper {version} with {N} plugins on {hostname}"

If `version_history.json` is absent, fall back to reading `{server-files-path}/paper.jar` manifest or asking the user.

---

## Step 2 — Create decision doc

Create `./minecraft-audits/` if it doesn't exist.

Create `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md` with this header:

```md
# PaperMC Server Audit — YYYY-MM-DD
Host: <production-ssh-alias> (<hostname>)
MC Version: <mc-version>
Paper Build: <build-number>
Plugins: <N>
Server Files: <server-files-path>
LGSM Script: <lgsm-script-path>
Staging Host: <staging-ssh-alias>
Staging Files: <staging-files-path>
```

---

## Step 3 — Invoke paper-check

Say: "Invoking `paper-check`."

Invoke `paper-check`, passing:
- Production SSH alias
- Server files path
- LGSM script path
- Staging SSH alias
- Staging files path
- Staging boot command
- Staging Java path
- MC version
- Current Paper build number
- Decision doc path (`./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`)

Paper-check chains to meta-refresh, which chains to version-refresh, which chains to executor. No further action needed from audit.

---

## Failure Handling

If SSH auto-detection fails (connection refused, no `version_history.json`, no `plugins/` directory), ask the user for manual input. If any downstream skill fails, it handles its own failure — no action needed from audit.

---

## Common Mistakes

- **Skipping inputs** — always ask for any missing values. Don't assume SSH aliases or paths.
- **Wrong decision doc path** — must be `./minecraft-audits/server-<hostname>-YYYY-MM-DD.md`, not in the server files directory or elsewhere.
- **Hardcoding host-specific paths** — all paths are runtime inputs resolved from the live server, never hardcoded.
- **Using server user as hostname** — derive `<hostname>` from `ssh <alias> hostname`, not from the SSH alias itself.
