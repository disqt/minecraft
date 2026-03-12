# Version Upgrade Plan Format

Use this format for the Step 3 upgrade plan.

---

## Format

```
## Upgrade Plan — {server-name}

### Summary
| Action | Count |
|--------|-------|
| Update available | N |
| Incompatible (no build) | N |
| Abandoned | N |
| Not found | N |
| Up to date | N |

### Proposed changes
| # | Action | Plugin | Version | Key changes | Notes |
|---|--------|--------|---------|-------------|-------|
| 1 | UPDATE | [EssentialsX](url) | 2.20.0 → 2.21.0 | [bugfix] economy dupe fix; [feature] new /nick formatting | — |
| 2 | MAJOR UPDATE | [LuckPerms](url) | 4.4.121 → 5.4.145 | [breaking] permissions format changed | review migration guide |
| 3 | FLAG | [WorldEdit](url) | 7.3.1 → none | — | no 1.21.1 build — check for update |
| 4 | CHECK DISCORD | [SomePlugin](url) | — | — | not found on Hangar or Modrinth |

### No changes needed (N plugins)
[CoreProtect](https://hangar.papermc.io/CORE/CoreProtect), [Multiverse-Core](https://hangar.papermc.io/Multiverse/Multiverse-Core), [ViaVersion](https://hangar.papermc.io/ViaVersion/ViaVersion), ... (collapsed, all linked)
```

## Action types

| Action | When to use |
|--------|-------------|
| `MAJOR UPDATE` | Different major version (e.g. 1.x → 2.x) |
| `UPDATE` | Different minor or patch version (e.g. 1.3.0 → 1.4.2) |
| `MINOR UPDATE` | Same version number, channel/build change only (e.g. alpha → beta, snapshot → release) |
| `FLAG` | Plugin exists but no build for target MC version — surface for user decision |
| `ABANDON` | No update in 12+ months, no newer MC builds |
| `CHECK DISCORD` | Not found on any source |

## Rules

- **Plugin names are always hyperlinked** — in every table row and in the collapsed "no changes" list. Link to wherever the plugin was found (Hangar preferred, Modrinth if not on Hangar, GitHub or plugin forum thread if that's the only source). Use the Source URL from the version agent's report.
- Every row has a link to the plugin page
- Version numbers from actual API responses — never guessed
- Open issue URLs go in Notes column
