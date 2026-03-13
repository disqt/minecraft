---
name: executor
description: Apply approved plugin changes to a PaperMC server — prepare staging, download plugins, research configs, boot-verify, and cut over to production with rollback safety.
---

REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents
REQUIRED SUB-SKILL: superpowers:systematic-debugging
REQUIRED SUB-SKILL: compat-check

# PaperMC Server Executor

Apply all approved changes from the decision doc. Prepares a staging server, verifies everything boots cleanly, then cuts over to production with player warning and rollback safety.

This is a FOREGROUND skill — the staging boot and cutover steps require user interaction.

## Inputs

All passed from version-refresh or provided directly. Ask for any not yet provided:

- **Decision doc path** — path to the audit decision doc
- **Production SSH alias** — e.g. `minecraft`. Used for backup, stop, apply, start.
- **Server files path** — absolute path on the production host, e.g. `/home/minecraft/serverfiles`
- **LGSM script path** — absolute path to the LGSM script on production, e.g. `/home/minecraft/mcserver`
- **Staging SSH alias** — e.g. `minecraft-staging`. Used for all staging operations.
- **Staging files path** — absolute path on the staging host, e.g. `/opt/minecraft/staging`
- **Staging boot command** — how to launch Paper on staging. Defaults to: `cd {staging-files-path} && {staging-java-path} -Xms512M -Xmx1536M -jar paper.jar nogui`
- **Staging Java path** — path to the Java binary on staging, e.g. `/usr/bin/java`
- **Target MC version** — e.g. `1.21.4`
- **Changelog digest** — accumulated from version-refresh changelog agents (may be empty if running executor standalone)

---

## Step 1 — Read decision doc

Read the decision doc at the provided path. Collect all approved changes across all sections:

**Paper decisions** (from `## Paper decisions`):
- Target Paper version (if upgrading)

**Meta decisions** (from `## Meta decisions`):
- `ADD` — new plugins to install
- `REPLACE` — plugins to swap (install new, remove old)
- `REMOVE` / `REDUNDANT` — plugins to delete

**Version decisions** (from `## Version decisions`):
- `UPDATE` — plugins to upgrade in place
- `MAJOR UPDATE` — same as UPDATE, note as potentially breaking

Only collect rows with `approved` in the Decision column. Rows with `skipped` or `cancelled` are ignored.

Summarise what you found before proceeding:
> Found N approved changes: M adds, P updates, Q removes, R replaces. Paper upgrade: yes/no.

---

## Step 2 — Prepare staging

### 2a. Create staging directory structure

```bash
ssh <staging-alias> "mkdir -p {staging-files-path}/plugins {staging-files-path}/logs"
```

### 2b. Rsync from production

Pull plugins and essential configs from production to staging:

```bash
# JAR files only — use --delete to remove stale JARs
ssh <prod-alias> "rsync -avz --delete {server-files-path}/plugins/*.jar <staging-alias>:{staging-files-path}/plugins/"

# Essential configs — do NOT use --delete
ssh <prod-alias> "rsync -avz {server-files-path}/server.properties <staging-alias>:{staging-files-path}/"
ssh <prod-alias> "rsync -avz {server-files-path}/bukkit.yml <staging-alias>:{staging-files-path}/"
ssh <prod-alias> "rsync -avz {server-files-path}/spigot.yml <staging-alias>:{staging-files-path}/"
ssh <prod-alias> "rsync -avz {server-files-path}/config/paper-world-defaults.yml <staging-alias>:{staging-files-path}/config/"
```

**Do NOT sync world data.** Staging only needs plugins and configs. World data is large and unnecessary for boot verification.

### 2c. Copy Paper JAR

```bash
ssh <prod-alias> "rsync -avz {server-files-path}/paper.jar <staging-alias>:{staging-files-path}/paper.jar"
```

If Paper version is being upgraded: download the target Paper JAR from the PaperMC API and place it at `{staging-files-path}/paper.jar` on staging. The current production `paper.jar` is NOT copied in this case.

```bash
# PaperMC API download:
# GET https://api.papermc.io/v2/projects/paper/versions/{mc-version}/builds
# Find latest stable build number, then:
# GET https://api.papermc.io/v2/projects/paper/versions/{mc-version}/builds/{build}/downloads/paper-{mc-version}-{build}.jar
ssh <staging-alias> "curl -L -o '{staging-files-path}/paper.jar' '{download-url}'"
```

---

## Step 3 — Dispatch parallel download agents

**REQUIRED SUB-SKILL: superpowers:dispatching-parallel-agents** — use it to dispatch and manage all download agents.

For every `ADD`, `REPLACE`, and `UPDATE` in the approved decisions, dispatch one download agent with `run_in_background: true`.

Read `./download-agent-prompt.md` (in this skill's directory) for the full agent spec. Pass each agent:

- Plugin name
- Action (`ADD`, `REPLACE`, or `UPDATE`)
- Source and Source URL (from the decision doc)
- Staging alias
- Staging plugins path (`{staging-files-path}/plugins`)
- MC version
- Old JAR filename (for `REPLACE` and `UPDATE` only)

**Wait for all download agents to complete before proceeding.**

If any download agent returns `FAILED`: report the failure to the user and stop. Ask how to proceed before continuing.

---

## Step 4 — Apply removals and dispatch config research agents

These two happen in parallel.

### 4a. Delete REMOVE/REDUNDANT JARs

For each `REMOVE` or `REDUNDANT` in approved decisions, delete the JAR from staging:

```bash
ssh <staging-alias> "rm -f '{staging-files-path}/plugins/{jar-filename}'"
```

If the JAR is not found on staging, note it and continue — it may have already been absent.

### 4b. Dispatch config research agents (parallel, background)

For each `ADD` or `REPLACE` in approved decisions, dispatch one config research agent with `run_in_background: true`.

Read `../meta-refresh/config-research-agent.md` (resolve this relative path against this skill's base directory before dispatching) for the agent spec.

Pass each agent: plugin name, target MC version, staging alias, staging files path.

**Wait for all config research agents to complete before Step 5.**

---

## Step 5 — Boot verification

Read `./staging-verification-agent.md` (in this skill's directory). Dispatch the staging verification agent (`run_in_background: false` — wait for result).

Pass:
- Staging alias
- Staging files path
- Staging Java path
- Staging boot command
- Expected plugins list: all `KEEP` plugins (infer from production JAR list minus removals) + all `ADD` + `REPLACE` target names + all `UPDATE` target names

### On FAIL

Report the full verification output to the user. Invoke `superpowers:systematic-debugging` to diagnose the cause. Do **NOT** proceed to cutover. Ask:

> 1. **Retry** — fix the issue and re-run verification
> 2. **Abandon** — abort, no production changes

### On WARN

Present the warnings to the user with the full verification output. Ask:

> Boot verification passed with warnings (listed above).
> 1. **Proceed** — continue to cutover despite warnings
> 2. **Abandon** — abort, no production changes

### On PASS

Continue to Step 6.

---

## Step 6 — Cutover

Present options to the user:

> Staging verified. Ready to cut over to production.
>
> 1. **Apply now** — check players, backup, stop production, apply changes, start
> 2. **Push to update folder** — upload new JARs to `plugins/update/` for next restart (plugins-only changes)
> 3. **Abandon** — discard staging, no production changes

### Option 1 — Apply now

Read `./cutover-agent-prompt.md` (in this skill's directory). Execute the full cutover procedure as described there.

Pass:
- Production SSH alias
- Staging SSH alias
- Server files path (production)
- Staging files path
- LGSM script path
- List of approved changes (adds, updates, removes, replaces)
- Paper JAR upgrade: yes/no + target version

If cutover returns `CUTOVER: ROLLBACK`: invoke `superpowers:systematic-debugging` with the rollback reason. Report to the user that production was restored from backup and must be investigated before retrying.

### Option 2 — Push to update folder

Only available when the approved changes are plugin-only (no Paper JAR upgrade, no REMOVE actions). If the changes include a Paper upgrade or plugin removals, inform the user that "Apply now" is required and skip this option.

**Important:** The `plugins/update/` folder only works for **updating existing plugins** — it matches JARs by **plugin name** (from `plugin.yml`), not by filename. This means:
- UPDATE and REPLACE actions work correctly (version-named JARs like `BlueMap-5.16-paper.jar` will replace `BlueMap-5.15-paper.jar`)
- **ADD actions do NOT work** via the update folder — new plugins have no existing plugin to match against, so Paper ignores them

Procedure:

1. Create the update directory on production:
   ```bash
   ssh <prod-alias> "mkdir -p {server-files-path}/plugins/update"
   ```

2. Upload UPDATE and REPLACE JARs to the update folder:
   ```bash
   rsync -avz -e ssh {staging-files-path}/plugins/<update-jar-1> {staging-files-path}/plugins/<update-jar-2> ... <prod-alias>:{server-files-path}/plugins/update/
   ```

3. Upload ADD JARs directly to `plugins/` (they won't load until restart, but they must be in the main folder):
   ```bash
   rsync -avz -e ssh {staging-files-path}/plugins/<new-jar-1> ... <prod-alias>:{server-files-path}/plugins/
   ```

4. Report what was pushed and note: "Changes will take effect on next server restart."

### Option 3 — Abandon

Discard staging. No production changes. Ask:
> 1. **Delete decision doc** — keep tidy
> 2. **Keep decision doc** — save for a future run

---

## Step 7 — Changelog digest

Read `./changelog-digest-format.md` (in this skill's directory). Compile the accumulated changelog from all phases using the format specified.

Append `## Changelog digest` to the decision doc.

---

## Step 8 — Write execution summary

Append `## Execution summary` to the decision doc with:

```md
## Execution summary

- **Staging verification:** PASS | WARN | FAIL
- **Cutover result:** SUCCESS | ROLLBACK | DEFERRED (pushed to update folder) | ABANDONED
- **Changes applied:**
  - Added: <list>
  - Updated: <list>
  - Removed: <list>
  - Replaced: <list>
  - Paper: <old version> → <new version> | no change
- **Warnings:** <list any staging warnings, or "none">
```

---

## Failure Handling

Invoke `superpowers:systematic-debugging` on any unexpected failure — SSH errors, rsync failures, API errors during Paper JAR download, config research agent failures, or cutover procedure errors not covered by known patterns.

If cutover fails: the rollback procedure in `./cutover-agent-prompt.md` is the recovery path. Do not attempt a second cutover without the user explicitly asking.

---

## Common Mistakes

- **Syncing world data to staging** — staging only needs plugins and configs, not worlds. World data is large and unnecessary for boot verification. Never rsync `world/`, `world_nether/`, `world_the_end/`, or any other world directories to staging.
- **Proceeding after backup failure** — the LGSM backup in the cutover procedure MUST succeed before stopping production. If backup fails, abort and tell the user. No exceptions.
- **Not checking player count** — always check before sending restart warnings. Skip the countdown if the server is empty.
- **Rsync --delete on config directories** — only use `--delete` on the plugins/ JAR directory. Never use `--delete` when syncing plugin config directories — it would wipe user data (permissions, settings, world configs).
- **rsync between two remote hosts** — rsync does not support remote-to-remote. Execute rsync from one host pulling from the other, or use a local intermediate. The cutover-agent-prompt.md shows the correct pattern.
- **Dispatching executor as a background agent** — this skill must run foreground. It requires user interaction at staging verification (WARN decision) and at cutover option selection.
- **Forgetting to pass expected plugins list to verification agent** — the staging-verification-agent needs the full expected plugin list to report missing plugins accurately. Derive it from: production plugins minus REMOVEs/REDUNDANTs, plus all ADDs and REPLACE targets.
