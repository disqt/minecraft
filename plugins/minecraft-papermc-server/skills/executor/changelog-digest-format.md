# Changelog Digest Format

## Format

```markdown
## Changelog Digest — <hostname> — YYYY-MM-DD

### Paper
<old version> -> <new version>
- [feature] ...
- [breaking] ...

### Plugins updated
**PluginName** old -> new
- [feature] ...
- [bugfix] ...

(repeat for each updated plugin)

### Plugins added
**PluginName** (new)
- one-line description

### Plugins removed
- PluginName — reason

### Config changes applied
| Plugin | Setting | Old | New | Reason |
```

## Rules

- Paper section only present if Paper version changed
- Changelog entries from changelog agents — do not fabricate
- Config changes from config-research agents
- Labels: [feature], [bugfix], [breaking], [perf] only
- Max 5 entries per plugin
- This digest is appended to the decision doc as the final section
