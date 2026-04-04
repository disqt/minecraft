---
name: chunk-refresh
description: Use when the user wants to refresh or regenerate chunk inspector data, update the chunk map, or make disqt.com/minecraft/chunks/ reflect the current server state. Triggers on "refresh chunks", "update chunk data", "regenerate chunks".
---

# Chunk Refresh

Regenerates the binary chunk data that powers the chunk inspector at `disqt.com/minecraft/chunks/`.

## Steps

1. **Deploy the generation script** to the Minecraft VPS:
```bash
scp "$(git rev-parse --show-toplevel 2>/dev/null || echo ../minecraft-frontend)/scripts/generate-chunk-data.py" minecraft:/home/minecraft/generate-chunk-data.py
```
If the minecraft-frontend repo isn't the current directory, find it at `C:/Users/leole/Documents/code/minecraft-frontend`.

2. **Run the script** on the VPS (parses region files, outputs Uint32 grids + metadata + markers):
```bash
ssh minecraft "python3 /home/minecraft/generate-chunk-data.py /home/minecraft/serverfiles /home/dev/minecraft-maps/data"
```
Takes 2-5 minutes. Output goes to `/home/dev/minecraft-maps/data/` served by nginx at `/minecraft/chunks-data/`.

3. **Verify** by checking the metadata:
```bash
ssh dev "cat /home/dev/minecraft-maps/data/overworld.json && echo '---' && cat /home/dev/minecraft-maps/data/nether.json"
```

4. **Report** chunk counts, visited counts, grid dimensions. Flag if counts changed significantly.

## Gotchas
- Does NOT require restarting the Minecraft server or Astro app
- Safe to run while server is live (reads region files, brief I/O load)
- Permission fix if needed: `ssh dev "chmod 777 /home/dev/minecraft-maps/data"`
