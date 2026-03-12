# Paper Compatibility Report Format

## Format

```markdown
## Paper Compatibility Report — <hostname>

### Current: Paper <version> (build <number>)
### Target:  Paper <version> (build <number>)

### Paper changelog highlights
- [feature] ...
- [breaking] ...

### Plugin compatibility
| # | Plugin | Current ver | Target build? | Status | Notes |
|---|--------|-------------|---------------|--------|-------|
| 1 | [AuthMe](https://hangar.papermc.io/AuthMe/AuthMe) | 5.6.0 | ✓ exact | READY | |
| 2 | [DHSupport](https://modrinth.com/plugin/dhsupport) | 0.12.0 | ✗ none | BLOCKER | no build for target |
| 3 | [BlueMap](https://hangar.papermc.io/BlueMap/BlueMap) | 5.15 | ~ minor | CHECK | minor-series match only |

### Verdict
READY: N/M plugins have builds for target
BLOCKER: N plugins — cannot upgrade until resolved
  — or —
ALL CLEAR: all M plugins have builds for target
```

## Status types

| Status | Meaning |
|--------|---------|
| READY | Plugin has a verified build for the target MC version |
| BLOCKER | No build exists for the target MC version — blocks Paper upgrade |
| CHECK | Minor-series match only — needs manual verification before upgrading |

## Rules

- All plugin names are hyperlinked to their Hangar or Modrinth page (Hangar preferred for Paper plugins)
- Version numbers and build numbers are from actual API calls — never guessed
- Sort order: BLOCKERs first, then CHECKs, then READY
- Paper changelog highlights use the label taxonomy: `[feature]`, `[bugfix]`, `[breaking]`, `[perf]`
- "Target build?" column values: `✓ exact` (precise MC version match), `~ minor` (minor-series match only), `✗ none` (no build found)
- The Verdict section collapses to `ALL CLEAR` when there are zero BLOCKERs and zero CHECKs
- If a plugin is not on Hangar or Modrinth, link to its GitHub releases page
