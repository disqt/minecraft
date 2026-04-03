---
name: villager-census
description: Run a villager population census on the PaperMC server. Collects entity data via SSH/tmux, parses POI files for beds, stores everything in SQLite, detects births and deaths since the last census, and opens an interactive HTML playground to inspect results and compare snapshots.
---

# Villager Census

Collect a full population snapshot of Minecraft villagers in a specified area, store it in a SQLite database, and produce an interactive visual report.

## Prerequisites

- A player must be online and near the target area (chunks must be loaded for entity data to be available)
- SSH access to the Minecraft server via `ssh minecraft`
- The server console is accessible via tmux at `/tmp/tmux-1000/pmcserver-bb664df1`

## Inputs

Ask for any not already known:

- **Area center** — defaults to Piwigord: x=3150, z=-950
- **Scan radius** — defaults to 300 blocks
- **Notes** — optional free-text annotation for this snapshot (e.g. "post-culling", "after bed expansion")

## Step 1 — Verify server access

1. Run `ssh minecraft "tmux -S /tmp/tmux-1000/pmcserver-bb664df1 send-keys -t pmcserver 'list' Enter"` and check the log for players online
2. If no players are online, STOP and tell the user: "No players online — chunks aren't loaded, so villager data is unavailable. Someone needs to be near Piwigord for the census to work."
3. Get the nearest player's position and verify they're within range of the target area

## Step 2 — Run the census pipeline

Run the Python census tool from the repo root:

```bash
cd villager-census && python census.py --db census.db --center-x 3150 --center-z -950 --radius 300
```

If this is the first run and `census.db` doesn't exist yet, first run the seeding script to reconstruct historical data from the March 30 culling:

```bash
# Download death logs
scp minecraft:/home/minecraft/serverfiles/logs/2026-03-30-3.log.gz /tmp/
gunzip -k /tmp/2026-03-30-3.log.gz
grep "died" /tmp/2026-03-30-3.log | grep "Villager" > /tmp/culling_deaths.txt

# Seed the database
cd villager-census && python census_seed.py --db census.db --deaths /tmp/culling_deaths.txt
```

The pipeline will:
1. Send `execute as @e[type=minecraft:villager,...] run data get entity @s` to the server console
2. Parse all entity data from the server log
3. Download POI region files and extract bed locations
4. Cross-reference beds with villager brain data
5. Write everything to the SQLite database
6. Detect births (new UUIDs) and deaths (missing UUIDs) since last snapshot

## Step 3 — Report summary

Print the census summary to the user:

```
## Census Summary — [date]

**Population:** [count] villagers ([+/-delta] from last census)
**Beds:** [count] ([claimed]/[total] claimed)
**Births:** [count] new villagers since last census
**Deaths:** [count] villagers disappeared since last census
**Homeless:** [count] villagers without a bed

### Profession breakdown
| Profession | Count | Change |
|---|---|---|
| farmer | 31 | +2 |
| ... | ... | ... |
```

## Step 4 — Launch playground

Invoke the `playground` skill to generate an interactive HTML viewer. The playground should:

1. Read the full database export from `villager-census/census.db` using `census.export_census_json()`
2. Embed the JSON data directly in the HTML
3. Include these views:
   - **Population timeline** — line chart of villager count and bed count across all snapshots
   - **Current census table** — sortable list of all villagers with profession, health, bed status, position
   - **Map view** — 2D scatter plot of villager positions, color-coded by profession, with bed markers
   - **Snapshot comparison** — dropdown to select two snapshots, shows births, deaths, movement, bed changes
   - **Villager detail** — click a villager to see full history across snapshots (position trail, profession changes, gossip)
4. Open the playground in the user's browser

## Database location

The SQLite database lives at `villager-census/census.db` in this repo. It is gitignored.
