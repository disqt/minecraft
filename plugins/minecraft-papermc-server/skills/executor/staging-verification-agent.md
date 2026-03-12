# Staging Boot Verification Agent Spec

Dispatched by the executor (foreground, `run_in_background: false`) after all plugins are downloaded to the staging server. Verifies PaperMC boots cleanly with all expected plugins before the user is asked to promote to production.

This agent makes completion claims about server state — it follows `superpowers:verification-before-completion` discipline: evidence before claims.

All commands run via SSH. Never run server-side commands locally.

---

## Inputs

- **Staging alias** — SSH alias for the staging server (e.g. `staging-minecraft`)
- **Staging files path** — absolute path to the PaperMC server directory on staging (e.g. `/opt/minecraft/staging`)
- **Staging java path** — path to the Java binary on staging (e.g. `/usr/bin/java`)
- **Staging boot command** — configurable launch command, defaults to:
  `cd {staging-files-path} && {staging-java-path} -Xms512M -Xmx1536M -jar paper.jar nogui`
- **Expected plugins** — list of plugin names that should load (from the decision doc — all KEEPs + ADDs + REPLACEs + UPDATEs)

Derived (do not ask):
- **Log path** — `{staging-files-path}/logs/latest.log`

---

## Procedure

### 1. Clear stale log

Delete the log file on staging if it exists from a previous boot:

```bash
ssh <staging-alias> "rm -f {staging-files-path}/logs/latest.log"
```

### 2. Launch the server

```bash
ssh <staging-alias> "nohup bash -c '{staging-boot-command}' > /dev/null 2>&1 &"
```

This boots PaperMC on the staging server in the background. The server will write its log to `{staging-files-path}/logs/latest.log`.

### 3. Wait for the log file to appear

Poll every 5s for up to 30s:

```bash
ssh <staging-alias> "test -f {staging-files-path}/logs/latest.log"
```

- If the file appears → continue to Step 4
- If 30s elapse with no log file → **FAIL** (`server did not start — no log produced`)

### 4. Monitor for crash or ready state

Poll the log file every 10s for up to 120s from first log appearance:

```bash
ssh <staging-alias> "cat {staging-files-path}/logs/latest.log"
```

**Crash indicators (any → stop polling, go to Step 5):**
- `---- Minecraft Crash Report ----`
- `[Server thread/ERROR]` followed by an exception or stack trace
- `Encountered an unexpected exception`
- `Failed to start the minecraft server`

**Ready indicator (stop polling early, go to Step 5):**
- `[Server thread/INFO]: Done (` — server finished loading

If a crash indicator or ready indicator is found → stop polling.
If 120s elapse with no crash indicator and no ready indicator → continue to Step 5 anyway.

### 5. Kill the process

```bash
ssh <staging-alias> "pkill -f 'paper.jar' 2>/dev/null; true"
```

Wait 3s, then verify it stopped:

```bash
ssh <staging-alias> "pgrep -f 'paper.jar' && echo 'still running' || echo 'stopped'"
```

If still running, force-kill:

```bash
ssh <staging-alias> "pkill -9 -f 'paper.jar' 2>/dev/null; true"
```

### 6. Verify with evidence

**Do NOT claim success yet.** Fetch the full log and run these checks:

```bash
ssh <staging-alias> "cat {staging-files-path}/logs/latest.log"
```

**6a. Check all expected plugins loaded:**
- Find lines matching `[Server thread/INFO]: \[PluginName\] Enabling PluginName v{version}` in the log
- Extract the plugin name from each such line
- Compare against the expected plugins list
- Report: `N/M expected plugins loaded` — list any missing

**6b. Scan for real errors:**
- Grep for `[Server thread/ERROR]`, `Exception`, and `FATAL` in the log
- **Filter out known harmless patterns:**
  - `[Server thread/WARN]` for deprecated API usage (e.g. `has registered a listener for ... using a deprecated method`)
  - `Ambiguity between arguments` (brigadier command registration noise)
  - Legacy material warnings (e.g. `Could not get provider for`)
  - `[Server thread/WARN]: Initializing Legacy Material Support` (expected on some plugin versions)
  - World-data-absence errors (see Step 6c)
- Report remaining errors with the actual log line

**6c. Check for world-data-absence warnings:**
- Grep for patterns like `Could not load world`, `world not found`, `No world named`, `Failed to load world`, or plugin-specific errors mentioning absent world data
- **These are WARN, not FAIL** — the staging server has no world data loaded. Plugins that reference worlds may log errors here but will work correctly on production where world data exists.
- Annotate each such item: `(staging server has no world data — plugin may work correctly on production)`

**6d. Check for crash:**
- Did any crash indicator appear in Step 4?

### 7. Return the report

---

## Decision Framework

| Evidence | Result |
|----------|--------|
| Crash indicator found | FAIL |
| Log never appeared in 30s | FAIL |
| Server process exited before ready, no ready marker | FAIL |
| All plugins loaded, 0 real errors, no crash | PASS |
| All plugins loaded, some real errors but no crash | WARN — report errors, let user decide |
| Missing plugins from expected list | WARN — report which plugins didn't load |
| World-data-absence errors only (no other errors) | WARN — note staging environment limitation |

**If FAIL:** Do NOT promote. Report evidence to the executor. Executor stops and asks the user.

**If WARN:** Report evidence. Executor presents warnings and asks user whether to proceed to production.

**If PASS:** Executor continues to report + promote prompt.

---

## Output Format

Return exactly this format:

```
## Boot Verification — <staging-alias>

Result: PASS | WARN | FAIL
Reason: <one line>

### Plugin loading
<N>/<M> expected plugins loaded
Missing: <list or "none">

### Errors
<N> real errors found
<list each error line, or "none">

### World-data warnings
<N> world-data-absence warnings (expected in staging)
<list each warning line, or "none">

### Log excerpt (last 20 lines)
<last 20 lines of latest.log>
```
