# Server Cutover Procedure

Apply verified changes from staging to production. This is a destructive operation — a backup is mandatory before proceeding.

## Inputs

- Production SSH alias
- Staging SSH alias
- Server files path (production)
- Staging files path
- LGSM script path
- List of changes to apply (from decision doc)
- Paper JAR upgrade (yes/no + target version)

## Procedure

### Step 1 — Check player count

```
ssh <prod-alias> "<lgsm-script> send 'list'"
# Parse output for player count
```

If zero players: skip to Step 3.

### Step 2 — Warn players

```
ssh <prod-alias> "<lgsm-script> send 'say Server restarting in 5 minutes for plugin updates'"
# Wait 4 minutes
ssh <prod-alias> "<lgsm-script> send 'say Server restarting in 1 minute'"
# Wait 1 minute
```

### Step 3 — Backup

```
ssh <prod-alias> "<lgsm-script> backup"
# Wait for completion — this MUST succeed before proceeding
# Verify backup exists in LGSM backup dir
```

### Step 4 — Stop production

```
ssh <prod-alias> "<lgsm-script> stop"
# Wait for server to fully stop (check process)
```

### Step 5 — Apply changes

NOTE: rsync does not support remote-to-remote. Execute rsync FROM production, pulling from staging. Alternatively, download staging files locally then upload to production.

```
# Sync plugins from staging to production (run on production host):
ssh <prod-alias> "rsync -avz --delete <staging-alias>:{staging-files-path}/plugins/*.jar {server-files-path}/plugins/"

# If Paper JAR upgrade:
ssh <prod-alias> "rsync -avz <staging-alias>:{staging-files-path}/paper.jar {server-files-path}/paper.jar"

# Sync config changes (only for plugins that had config research)
# For each plugin with config changes — do NOT use --delete on config dirs:
ssh <prod-alias> "rsync -avz <staging-alias>:{staging-files-path}/plugins/<PluginName>/ {server-files-path}/plugins/<PluginName>/"
```

### Step 6 — Start production

```
ssh <prod-alias> "<lgsm-script> start"
```

### Step 7 — Monitor boot

```
# Monitor {server-files-path}/logs/latest.log for 90 seconds
# Check for crash indicators (same as staging verification)
# Verify all expected plugins loaded
```

### Step 8 — Report

If boot succeeds: report SUCCESS with changelog digest
If boot fails: proceed to rollback

## Rollback procedure

If production fails to start after cutover:

1. `ssh <prod-alias> "<lgsm-script> stop"` — Ensure fully stopped
2. Restore from LGSM backup taken in Step 3
3. `ssh <prod-alias> "<lgsm-script> start"`
4. Verify production is back online with original plugins
5. Report ROLLBACK with error details — user must investigate before retrying

## Output

```
CUTOVER: SUCCESS — {N} plugins updated, {N} added, {N} removed
  or
CUTOVER: ROLLBACK — {reason}. Production restored to pre-cutover state.
```

## Common Mistakes

- **Never rsync --delete on plugin config directories** — only use --delete on the plugins/ JAR directory. Config dirs contain user data (permissions, settings) that must be preserved.
- **Always verify backup completion** — if the LGSM backup fails or times out, abort the cutover. Do not proceed without a safety net.
- **Don't skip player count check** — always check before sending restart warnings. An empty server can be restarted immediately.
- **rsync is not remote-to-remote** — execute rsync from production pulling from staging, not between two remote hosts.
