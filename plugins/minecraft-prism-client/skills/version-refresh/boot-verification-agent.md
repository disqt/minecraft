# Boot Verification Agent Spec

Dispatched by the executor (foreground, `run_in_background: false`) after all mods are installed. Verifies the new instance boots cleanly before the user is asked to promote it.

This agent makes completion claims about instance state — it follows `superpowers:verification-before-completion` discipline: evidence before claims.

---

## Inputs

- **Instance name** — e.g. `1.21.11 v2.0.beta`
- **Instance path** — `{PRISM_INSTANCES}/<instance-name>/`
- **Prism exe** — `{PRISM_EXE}` (resolved by parent)
- **Expected mods** — list of mod names that should be loaded (from the decision doc — all KEEPs + ADDs + REPLACEs + UPDATEs)

Derived (do not ask):
- **Log path** — `<instance-path>/.minecraft/logs/latest.log`

---

## Procedure

### 1. Clear stale log

Delete `<log-path>` if it exists from a previous boot.

### 2. Launch the instance

```bash
"{PRISM_EXE}" --launch "<instance-name>" &
```

This uses Prism's own launch path — it reads the instance's Java path, JVM args, memory, and classpath automatically.

### 3. Wait for the log file to appear

Poll `<log-path>` every 5s for up to 30s.

- If the file appears → continue to Step 4
- If 30s elapse with no log file → **FAIL** (`launcher did not start — no log produced`)

### 4. Monitor for crash

Poll the log file every 10s for up to 90s from first log appearance:

**Crash indicators (any → FAIL immediately):**
- `---- Minecraft Crash Report ----`
- `Game crashed! Crash report saved to:`
- `FATAL ERROR`
- `[main/ERROR]` followed by an exception or stack trace on the next line

If a crash indicator is found → stop polling, go to Step 5.
If 90s elapse with no crash indicator → continue to Step 5.

### 5. Kill the process

**Windows:**
```bash
taskkill //F //IM prismlauncher.exe 2>/dev/null
taskkill //F //IM javaw.exe 2>/dev/null
```

**Linux/macOS:**
```bash
pkill -f prismlauncher 2>/dev/null
pkill -f "java.*minecraft" 2>/dev/null
```

### 6. Verify with evidence

**Do NOT claim success yet.** Run these checks and collect evidence:

**6a. Check all expected mods loaded:**
- Find the `Reloading ResourceManager:` line in the log
- Parse the comma-separated mod list from that line
- Compare against the expected mods list
- Report: `N/M expected mods loaded` — list any missing

**6b. Scan for real errors:**
- Grep for `ERROR` and `Exception` in the log
- **Filter out known harmless patterns:**
  - `refmap.*could not be read` (Mixin refmap warnings)
  - `Error loading class:` + `ClassNotFoundException` (optional mod compat)
  - `pack metadata` format warnings
  - `EMF.*already exists, overwriting`
  - `DH` (Distant Horizons) noise
- Report remaining errors with the actual log line

**6c. Check for crash:**
- Did any crash indicator appear in Step 4?

### 7. Return the report

---

## Decision Framework

| Evidence | Result |
|----------|--------|
| Crash indicator found | FAIL |
| Log never appeared in 30s | FAIL |
| Process exited before 90s, no success marker | FAIL |
| All mods loaded, 0 real errors, no crash | PASS |
| All mods loaded, some real errors but no crash | WARN — report errors, let user decide |
| Missing mods from expected list | WARN — report which mods didn't load |

**If FAIL:** Do NOT promote. Report evidence to the executor. Executor stops and asks the user.

**If WARN:** Report evidence. Executor presents warnings and asks user whether to proceed.

**If PASS:** Executor continues to report + promote prompt.

---

## Output Format

Return exactly this format:

```
## Boot Verification — <instance-name>

Result: PASS | WARN | FAIL
Reason: <one line>

### Mod loading
<N>/<M> expected mods loaded
Missing: <list or "none">

### Errors
<N> real errors found
<list each error line, or "none">

### Log excerpt (last 20 lines)
```
<last 20 lines of latest.log>
```
```
