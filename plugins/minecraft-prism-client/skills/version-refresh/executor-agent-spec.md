# Executor Agent Spec

Background agent dispatched after version-refresh Step 5. Receives: decision doc path, instance name, MC version, modloader, and resolved paths (`{PRISM_INSTANCES}`, `{PRISM_EXE}`).

**Model note:** This agent makes many judgment calls (version lookups, naming, failure handling). For best results, run the parent session with Opus (`/model`).

**REQUIRED SUB-SKILL:** superpowers:dispatching-parallel-agents — use for Steps 6 and 7 (download agents, config research agents).

**REQUIRED SUB-SKILL:** superpowers:systematic-debugging — invoke when any step produces unexpected results (download failures, config errors, boot verification failures not covered by known patterns) before retrying or escalating.

---

## Inputs

These are passed from the parent skill. Never hardcode OS-specific paths.

- **Decision doc path** — path to the audit decision doc
- **Instance name** — e.g. `1.21.11 v1.1`
- **MC version** — e.g. `1.21.11`
- **Modloader** — e.g. `Fabric`
- **`{PRISM_INSTANCES}`** — resolved Prism instances directory
- **`{PRISM_EXE}`** — resolved Prism executable path
- **Publish config** *(optional)* — VPS SSH alias, remote dir, and base URL for modpack hosting. If not provided, skip Step 12.

---

## Steps

### 1. Read the decision doc

Collect all approved meta decisions (`## Meta decisions`) and approved version decisions (`## Version decisions`).

### 2. Ask the user for version increment type

Assess the approved changes and recommend one:

- **Minor increment** (e.g. `v1.1` → `v1.2.beta`): few changes, mostly bugfixes or version bumps, no significant UX difference
- **Major increment** (e.g. `v1.1` → `v2.0.beta`): many mods added/replaced, noticeable change in audio/performance/UX

Present your recommendation with a one-line justification, then ask:
> Recommended: **major** — 13 of 31 mods changing (11 adds, 2 replaces), significant new audio and performance profile. Use **major** or **minor**?

Wait for the user's response before proceeding.

### 3. Clone the instance

**Windows:**
```
xcopy /E /I /H "{PRISM_INSTANCES}/<old-instance>" "{PRISM_INSTANCES}/<new-instance>"
```

**Linux/macOS:**
```bash
cp -a "{PRISM_INSTANCES}/<old-instance>" "{PRISM_INSTANCES}/<new-instance>"
```

**Naming rules:**
- Minor: bump the minor version digit — `v1.1` → `v1.2.beta`, `v2.3` → `v2.4.beta`
- Major: bump the major version, reset minor to 0 — `v1.1` → `v2.0.beta`, `v2.3` → `v3.0.beta`
- **NEVER append `(2)` or any copy suffix** — that's a Prism artifact. If the target `.beta` already exists, delete it first (it's from an aborted run — beta instances are disposable by design).

### 4. Tell the user

State the new instance name and remind them to refresh Prism (Ctrl+R).

### 5. Delete removals

For each `REMOVE` or `REDUNDANT`: delete the JAR (and `.disabled` twin if present) from the new instance `.minecraft/mods/`. Sequential, instant.

### 6. Dispatch parallel download agents

For every `ADD`, `REPLACE`, and `UPDATE` in the decision doc, dispatch one download agent with `run_in_background: true`.

Read `./download-agent-prompt.md` (in this skill's directory) for the agent spec and the variables to inject per agent.

**Wait for all download agents to complete before proceeding.**

If any download agent returns `FAILED`: report the failure to the user and stop. Ask how to proceed before continuing.

### 7. Dispatch config research agents + apply ENABLEs

These two can happen concurrently:

- **Config research (parallel):** For each `ADD` or `REPLACE`, dispatch one config research agent with `run_in_background: true`. Read `../meta-refresh/config-research-agent.md` for the agent spec. Resolve this relative path against this skill's base directory before dispatching.
- **ENABLEs (instant):** For each `ENABLE`, rename `<mod>.jar.disabled` → `<mod>.jar`.

### 8. Wait for all config research agents to complete.

### 9. Verify the client boots

Dispatch a boot verification agent (`run_in_background: false`, wait for result).

Read `./boot-verification-agent.md` (in this skill's directory) for the agent spec. Pass: new instance path, `{PRISM_EXE}`, MC version.

- If boot **fails**: report the crash log excerpt and stop. Do NOT promote. Ask the user how to proceed.
- If boot **passes**: continue to step 10.

### 10. Report

Summarise: changes applied (meta + version), config files written, boot result.

Then tell the user:
> Instance `<name>.beta` is ready and verified. Test it yourself, then reply **"promote"** to rename it to `<name-without-.beta>` (e.g. `1.21.11 v2.0`).

### 11. On "promote"

Rename the instance folder from `<name>.beta` to `<name-without-.beta>`. Remind user to refresh Prism (Ctrl+R).

### 12. Publish the modpack (optional)

**Skip this step if no publish config was provided.**

After promote, zip and upload the instance so friends can download it. Requires: `{VPS_SSH}` (SSH alias), `{VPS_PRISM_DIR}` (remote dir), `{MODPACK_BASE_URL}` (public URL).

**12-pre. Update modpack-version.txt:**

Extract the version number from the instance name (e.g. `1.21.11 v2.2` → `2.2`) and write it to `{PRISM_INSTANCES}/<instance-name>/.minecraft/modpack-version.txt`. This file is read by the disqt-version Fabric mod to report the client's modpack version to the server.

```bash
echo "<version>" > "{PRISM_INSTANCES}/<instance-name>/.minecraft/modpack-version.txt"
```

**12a. Zip with exclusions:**

```bash
cd "{PRISM_INSTANCES}"
zip -r "<instance-name>.zip" "<instance-name>/" \
  -x "*Distant_Horizons_server_data*" \
  -x "*screenshots*" \
  -x "*saves*" \
  -x "*downloads*" \
  -x "*.mixin.out*" \
  -x "*debug*" \
  -x "*logs*"
```

On Windows with 7z:
```bash
cd "{PRISM_INSTANCES}"
7z a -tzip "<instance-name>.zip" "<instance-name>/" \
  -xr!"Distant_Horizons_server_data" \
  -xr!"screenshots" \
  -xr!"saves" \
  -xr!"downloads" \
  -xr!".mixin.out" \
  -xr!"debug" \
  -xr!"logs"
```

**12b. Upload to VPS:**

```bash
scp "{PRISM_INSTANCES}/<instance-name>.zip" {VPS_SSH}:{VPS_PRISM_DIR}
```

**12c. Update the `latest.zip` symlink:**

```bash
ssh {VPS_SSH} "cd {VPS_PRISM_DIR} && ln -sf '<instance-name>.zip' latest.zip"
```

**12d. Update `manifest.json`:**

Read the current manifest from the VPS, prepend the new version to the `versions` array, update `latest`, and write it back. Also read `## Changelog summary` from the decision doc and include it as a `"changelog"` array.

First, extract changelog lines from the decision doc locally:

```python
# Run locally to extract changelog lines
changelog = []
with open('<decision-doc-path>') as f:
    in_changelog = False
    for line in f:
        if line.strip() == '## Changelog summary':
            in_changelog = True
            continue
        if in_changelog:
            if line.startswith('## '):
                break
            stripped = line.strip()
            if stripped.startswith('- '):
                changelog.append(stripped[2:])
```

Then pass the changelog to the remote manifest update:

```bash
ssh {VPS_SSH} "python3 -c \"
import json, os
path = '{VPS_PRISM_DIR}/manifest.json'
data = json.load(open(path)) if os.path.exists(path) else {'latest':{}, 'versions':[]}
changelog = <changelog-json-array>
entry = {
  'version': '<instance-name>',
  'file': '<instance-name>.zip',
  'date': '$(date +%Y-%m-%d)',
  'mc': '<mc-version>',
  'modloader': '<modloader>',
  'size': '<size in MB> MB',
  'changelog': changelog
}
data['latest'] = entry
data['versions'].insert(0, entry)
json.dump(data, open(path,'w'), indent=2)
print('manifest updated')
\""
```

Replace `<changelog-json-array>` with the JSON-encoded list (e.g. `["Added Ping Wheel", "Updated shaders"]`). If no changelog section exists in the decision doc, use `[]`.

Compute `<size in MB>` from the zip file size before uploading.

**12e. Cleanup — keep last 3 zips (exclude symlink):**

```bash
ssh {VPS_SSH} "cd {VPS_PRISM_DIR} && ls -t *.zip | grep -v latest.zip | tail -n +4 | while IFS= read -r f; do rm -f \"\\\$f\"; done"
```

**12f. Report the URLs:**

> Modpack published: **{MODPACK_BASE_URL}**
> - Latest (stable link): `{MODPACK_BASE_URL}/latest.zip`
> - This version: `{MODPACK_BASE_URL}/<instance-name>.zip`
