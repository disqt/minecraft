# Upgrade Plan Format

Use this format for the meta-refresh upgrade plan presented to the user.

---

## Format

```
## Upgrade Plan — {server-name}

### Summary
| Action | Count |
|--------|-------|
| Replace | N |
| Add | N |
| Remove | N |
| Keep | N |

### Proposed changes
| # | Action | Plugin | Current | Alternative | DL | Compat | Pros | Cons | Links |
|---|--------|--------|---------|-------------|-----|--------|------|------|-------|
| 1 | REPLACE | [EssentialsX](url) | 2.20.1 | [CMI](url) | 3M → 1.2M | Paper 1.21.4 ✓ | more integrated economy/home/warp; active dev | lower DL count; paid add-ons | [EssentialsX](url) [CMI](url) |
| 2 | ADD | [Chunky](url) | — | — | 4M | Paper 1.21.4 ✓ | pre-generates chunks; reduces lag spikes for new players | none | [link](url) |
| 3 | REMOVE | [OldPlugin](url) | 1.0.0 | — | 12k | no 1.21.4 build | abandoned; last update 2022 | — | [link](url) |

### Wildcards
Plugins outside the vanilla+ server profile. Mention with clear label — user says `approve W1` to promote to ADD.

| # | Plugin | Category | DL | Why it's interesting | Links |
|---|--------|----------|----|----------------------|-------|
| W1 | [DynMap](url) | Web map | 8M | Live browser map of the world; useful for public servers | [link](url) |
| W2 | [GriefPrevention](url) | Land claim | 5M | Self-serve land claiming; reduces grief without admin overhead | [link](url) |

### No changes needed (N plugins)
[paper](url), [luckperms](url), [vault](url), ... (collapsed)
```

## Action types

| Action | When to use |
|--------|-------------|
| `REPLACE` | Clearly better alternative exists AND is compat-confirmed |
| `ADD` | Strong plugin missing from the server, compat-confirmed including all deps |
| `REMOVE` | Plugin with no build for target MC/Paper version, or abandoned with a confirmed successor |
| `KEEP` | Current plugin is best or near-best for this slot |

Note: there is no `ENABLE` action — server JARs are not stored as `.disabled` files.

## Wildcards

Wildcards are plugins that fall outside the server's current design goals (e.g. web maps, economy systems, land claiming, minigame frameworks) but are worth surfacing because they are popular, well-maintained, or solve a real problem the server may face.

- Numbered **W1, W2, …** — a separate namespace from the main proposed changes table
- User says `approve W1` to promote a wildcard to a full `ADD` entry
- Do not include wildcards that are clearly incompatible with the target MC/Paper version

## Rules

- **Plugin names are always hyperlinked** — in every table row and in the collapsed "no changes" list. Link to wherever the plugin was found (Hangar preferred, Modrinth or GitHub if that's the only source).
- Real links for every plugin and every alternative — no guessed URLs
- Stats (DL counts, last-updated dates) from actual API calls — never guessed
- Compat column: confirm via paper-check or Hangar/Modrinth API — format as `Paper X.Y.Z ✓` or `unconfirmed`
- Pros/cons: factual, max 2-3 points, no padding
- If uncertain: say so and link to where the user can verify
- Sort order: REPLACE first, ADD second, REMOVE last; KEEP entries go in the collapsed section
