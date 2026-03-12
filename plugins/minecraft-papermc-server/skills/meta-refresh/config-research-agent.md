# Config Research Agent

Dispatched by the executor (end of version-refresh) for every plugin that was added or used as a replacement. Run in background (`run_in_background: true`), one agent per plugin.

---

## Steps

1. **Find source repo:** `GET https://api.modrinth.com/v2/project/{id}` → read `source_url`
2. **Locate config file in repo:** check `src/main/resources/`, `/config/`, look for `.yml` / `.yaml` / `.json` / `.toml` config files
3. **If no config file found:** search source for classes named `Config`, `Settings`, `Options`, `PluginConfig` — read fields and defaults
4. **For each config option:** understand name, default, valid values, and effect
5. **Reason about optimal values** for a vanilla+ PaperMC server — minimize resource usage, optimize performance for 5–20 players, keep sensible defaults, no gameplay changes beyond vanilla+
6. **Write tuned config file** via SSH to `{server-files-path}/plugins/<PluginName>/config.yml` (or `.yaml` / `.json` as appropriate) on the staging server
7. **Return report:**

```
## Config Report: {plugin-name}

- **Source repo:** {url}
- **Config file written:** {path, e.g. plugins/Chunky/config.yml}

### Settings changed from default
| Setting | Default | Applied | Reason |
|---------|---------|---------|--------|
| max-threads | auto | 2 | cap threads to leave headroom for game loop on small server |

### Settings left at default
| Setting | Value | Reason kept |
|---------|-------|-------------|
| verbose-logging | false | default is already appropriate |

### Notes
{any warnings, e.g. "no config file found — plugin uses hardcoded defaults, nothing to tune"}
```

---

## Tuning Goals

- **Performance:** prefer settings that reduce CPU and memory pressure. PaperMC servers for 5–20 players do not need aggressive parallelism; cap worker threads rather than leaving them on `auto`.
- **Vanilla+:** do not enable features that expose non-vanilla information to players (e.g. admin-facing metrics endpoints are fine; player-facing overlays are not).
- **YAML format:** most Paper plugins use YAML. Preserve comments when rewriting configs if the plugin emits them. Do not collapse multi-line values.
- **SSH write path:** configs live on the remote server. Use `ssh minecraft "cat > {server-files-path}/plugins/<PluginName>/config.yml" << 'EOF' ... EOF` or `scp` to write files. Never write to the local filesystem.
