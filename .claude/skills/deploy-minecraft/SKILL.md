---
name: deploy-minecraft
description: Use when deploying the minecraft-frontend Astro app to production. Triggers on "deploy", "push to prod", "ship it", or when changes to disqt.com/minecraft/ need to go live.
---

# Deploy Minecraft

Deploys the minecraft-frontend Astro SSR app to `disqt.com/minecraft/`.

## Steps

1. **Check for uncommitted changes** before pushing:
```bash
cd C:/Users/leole/Documents/code/minecraft-frontend
git status --short
```
If there are uncommitted changes, ask the user whether to commit first or deploy as-is.

2. **Push the current branch** to GitHub:
```bash
git push origin HEAD
```

3. **Deploy on VPS** — pull, build, restart (sequential, never overlap):
```bash
ssh dev "cd /home/dev/minecraft-frontend && git pull && npm run build && sudo systemctl restart minecraft-frontend"
```
NEVER run overlapping build commands — causes OOM crash on the VPS.

4. **Verify** the site loads:
```bash
curl -sI "https://disqt.com/minecraft/" | head -3
curl -sI "https://disqt.com/minecraft/chunks/" | head -3
```
Expect HTTP 200 on both.

5. **Report** success with the live URL.

## Gotchas
- VPS branch must match what you push. Switch if needed: `ssh dev "cd /home/dev/minecraft-frontend && git fetch origin && git checkout <branch>"`
- If `npm run build` fails, do NOT restart the service — fix the build error first
- Service runs on port 4322, proxied by nginx at `/minecraft/`
