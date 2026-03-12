---
name: prism-audit
description: Use when the user wants to do a full refresh of their Prism Launcher modset in one session — both auditing mod quality (replacing outdated or superseded mods) and updating all mod versions to their latest compatible builds.
---

REQUIRED SUB-SKILL: meta-refresh
REQUIRED SUB-SKILL: version-refresh

# Minecraft Prism Client Audit

Entry point for a full modset refresh. Creates the shared decision doc, then invokes meta-refresh. The skills chain automatically: meta-refresh → version-refresh → background executor.

## Paths

Detect the user's OS and resolve these automatically. Ask only if detection fails.

| Variable | Windows | Linux | macOS |
|----------|---------|-------|-------|
| `{PRISM_INSTANCES}` | `%APPDATA%/PrismLauncher/instances/` | `~/.local/share/PrismLauncher/instances/` | `~/Library/Application Support/PrismLauncher/instances/` |
| `{PRISM_EXE}` | `prismlauncher.exe` (find via `where` or check `%LOCALAPPDATA%/Programs/PrismLauncher/`) | `prismlauncher` (in PATH) | `/Applications/PrismLauncher.app/Contents/MacOS/prismlauncher` |

Pass resolved paths to all sub-skills. Sub-skills should never hardcode OS-specific paths.

## Inputs

Ask for any of these not already provided:

- **Prism instance name** — auto-detect by listing `{PRISM_INSTANCES}`
- **Target MC version** — e.g. `1.21.11`
- **Modloader** — default: `Fabric`
- **Player profile** — default: vanilla+ Fabric client (performance, subtlety, no gameplay changes)
- **Reference packs** — default: DisruptiveBuilds REFINED (`dbs-minecraft-refined`) and PLUS (`dbs-minecraft-plus`) on Modrinth
- **Server SSH host** *(optional)* — e.g. `minecraft`. Used to check which server-side companion mods are active, affecting client mod recommendations.

---

## Flow

```
prism-audit
  └─ creates decision doc
  └─ invokes meta-refresh
       └─ research → upgrade plan → user approves → writes meta decisions to doc
       └─ invokes version-refresh
            └─ research → upgrade plan → user approves → appends version decisions to doc
            └─ dispatches background executor
                 └─ clones instance → applies meta changes → applies version updates → config research
```

---

## Step 1 — Create decision doc

Create `./minecraft-audits/` if it doesn't exist.

Create `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md` with this header:

```md
# Minecraft Audit — YYYY-MM-DD
Instance: <name>
MC Version: <version>
Modloader: <loader>
```

---

## Step 2 — Invoke meta-refresh

Say: "Invoking `meta-refresh`."

Invoke `meta-refresh`, passing:
- Instance name
- MC version
- Modloader
- Player profile
- Server SSH host (if provided)
- Decision doc path (`./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`)

Meta-refresh chains to version-refresh, which chains to the executor. No further action needed from audit.

---

## Common Mistakes

- **Skipping inputs** — always ask for any missing values. Don't assume MC version or instance name.
- **Wrong decision doc path** — must be `./minecraft-audits/prism-<instance-name>-YYYY-MM-DD.md`, not in the instance directory or elsewhere.
