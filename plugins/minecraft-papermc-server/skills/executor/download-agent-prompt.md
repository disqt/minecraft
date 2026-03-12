# Download Agent Prompt Template

One agent per plugin. Dispatched in parallel by the executor. Downloads and installs one plugin JAR into the staging server's plugins directory via SSH.

---

## Inputs (injected per agent)

- **Plugin name:** {plugin-name}
- **Action:** {ADD | REPLACE | UPDATE}
- **Source:** {Hangar | Modrinth | CurseForge | GitHub}
- **Source URL:** {direct link to plugin page — no searching needed}
- **Staging alias:** {SSH alias for the staging server, e.g. `minecraft-staging`}
- **Staging plugins path:** {absolute path to plugins directory on staging server, e.g. `/opt/minecraft/staging/plugins`}
- **MC version:** {e.g. 1.21.4}
- **Old JAR filename:** {exact filename to delete — only for REPLACE and UPDATE; omit for ADD}

---

## Procedure

### 1. Find the download URL

Try sources in order: **Hangar first**, then Modrinth, CurseForge, GitHub.

**If Source is Hangar:**
```
GET https://hangar.papermc.io/api/v1/projects/{slug}/versions/{version}
```
Read `downloads.PAPER.downloadUrl` for the direct download URL. The filename is the last path segment of the download URL.

**If Source is Modrinth:**
```
GET https://api.modrinth.com/v2/project/{slug}/version?game_versions=["{mc-version}"]&loaders=["paper"]
```
Take the first result (latest compatible). Read `files[0].url` for the direct download URL and `files[0].filename` for the target filename.

**If Source is CurseForge:**
Fetch the plugin's file list page at the Source URL. Find the latest file compatible with the MC version. Extract the direct download URL.

**If Source is GitHub:**
```
GET https://api.github.com/repos/{owner}/{repo}/releases/latest
```
Find the asset whose filename matches `*{mc-version}*` (or the plain JAR if no version-specific asset exists). Read `browser_download_url`.

### 2. Download the JAR to staging

Execute via SSH:

```bash
ssh {staging-alias} "curl -L -o '{staging-plugins-path}/{filename}' '{download-url}'"
```

### 3. Remove old JAR (REPLACE and UPDATE only)

Execute via SSH before downloading the new JAR:

```bash
ssh {staging-alias} "rm '{staging-plugins-path}/{old-jar-filename}'"
```

If the old JAR is not found, proceed with the install anyway and note it in output.

---

## Decision Framework

| Situation | Response |
|-----------|----------|
| No compatible version found for MC version | Return `FAILED: no {mc-version} Paper build found` |
| Download fails (HTTP error, network) | Retry once. If still fails, return `FAILED: download error {status}` |
| Old JAR not found for REPLACE/UPDATE | Proceed with install anyway. Note in output: `(old JAR not found — skipped delete)` |
| Multiple files in release (e.g. sources jar) | Pick the one without `-sources` or `-dev` in the filename |
| SSH command fails | Return `FAILED: SSH error — {error message}` |

---

## Output Format

Return exactly one of:

```
INSTALLED: {filename}
```

or

```
FAILED: {reason}
```
