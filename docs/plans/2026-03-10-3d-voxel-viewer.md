# 3D Voxel Viewer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current 2D grid viewer with a Three.js 3D voxel renderer that shows redstone builds as textured Minecraft blocks with orbit controls and a Y-axis cross-section slider.

**Architecture:** Single self-contained HTML file. Three.js loaded via CDN importmap. Voxel data from the same `BUILD_DATA_JSON` format. Merged geometry with face culling (Three.js official voxel approach). OrthographicCamera for a BlueMap-style default view. Clipping plane on Y-axis for cross-sections.

**Tech Stack:** Three.js r170+ (CDN via unpkg), OrbitControls, built-in clipping planes, PrismarineJS block textures as texture atlas.

---

## Context

### Current state
- Viewer template: `plugins/minecraft-prism-client/skills/redstone/assets/viewer-template.html` (~95KB)
- 201 base64-encoded PrismarineJS textures in `const BLOCK_TEXTURES = {...}`
- `BUILD_DATA_JSON` format: layers array, each with a grid of `"block_id:direction"` cells
- `FACE_MAP` maps blocks to per-face textures (top/bottom/side/front/nsew)
- Served at `https://disqt.com/minecraft/redstone/` via nginx on the VPS

### Key files
- Template: `plugins/minecraft-prism-client/skills/redstone/assets/viewer-template.html`
- Test page: uploaded via `scp <file> dev:/home/dev/redstone-viewer/<name>.html`
- Textures scraper: `/tmp/mc-textures/scrape_all.py`

### What the 3D viewer replaces
The current 2D viewer has top-down and side views. The 3D viewer replaces both with a single orbitable 3D scene plus a Y-slider for cross-sections. The HTML still uses the same `{{PLACEHOLDER}}` template system and `BUILD_DATA_JSON` data format.

---

## Chunk 1: Texture Atlas

The 201 individual base64 textures need to be combined into a single texture atlas image for Three.js. Each texture is 16x16. We arrange them in a grid and build a lookup table mapping block texture names to atlas UV coordinates.

### Task 1: Build texture atlas from existing base64 textures

**Files:**
- Create: `/tmp/build-atlas.py` (one-time script)
- Output: `/tmp/mc-textures/atlas.png` + `/tmp/mc-textures/atlas-map.json`

- [ ] **Step 1: Write the atlas builder script**

The script reads the existing `block_textures_full.js` (or extracts from the template), decodes each base64 PNG, tiles them into a grid (e.g., 16 columns x 13 rows = 208 slots for 201 textures), and outputs:
- `atlas.png`: the combined image (256x208 pixels)
- `atlas-map.json`: `{ "texture_name": { "col": 0, "row": 0 }, ... }`

```python
import json, base64, struct
from PIL import Image
from io import BytesIO

COLS = 16  # textures per row
TILE = 16  # pixels per texture

# Load textures from the JS file
with open('/tmp/mc-textures/block_textures_full.js') as f:
    raw = f.read()
    # Extract JSON between { and };
    start = raw.index('{')
    end = raw.rindex('}') + 1
    textures = json.loads(raw[start:end])

names = sorted(textures.keys())
rows = (len(names) + COLS - 1) // COLS
atlas = Image.new('RGBA', (COLS * TILE, rows * TILE), (0, 0, 0, 0))
atlas_map = {}

for i, name in enumerate(names):
    col, row = i % COLS, i // COLS
    data = base64.b64decode(textures[name].split(',')[1])
    img = Image.open(BytesIO(data)).convert('RGBA').resize((TILE, TILE), Image.NEAREST)
    atlas.paste(img, (col * TILE, row * TILE))
    atlas_map[name] = {"col": col, "row": row}

atlas.save('/tmp/mc-textures/atlas.png')
with open('/tmp/mc-textures/atlas-map.json', 'w') as f:
    json.dump(atlas_map, f)
print(f"Atlas: {COLS*TILE}x{rows*TILE}, {len(names)} textures")
```

- [ ] **Step 2: Run it**

```bash
cd /tmp/mc-textures && python3 build-atlas.py
```

Expected: `atlas.png` and `atlas-map.json` created.

- [ ] **Step 3: Base64-encode the atlas for embedding**

```bash
echo "const ATLAS_DATA = 'data:image/png;base64,$(base64 -w0 /tmp/mc-textures/atlas.png)';" > /tmp/mc-textures/atlas-data.js
```

- [ ] **Step 4: Generate the atlas UV map as JS**

```python
import json
with open('/tmp/mc-textures/atlas-map.json') as f:
    m = json.load(f)
# Output as JS constant
with open('/tmp/mc-textures/atlas-uv-map.js', 'w') as f:
    f.write(f"const ATLAS_COLS = 16;\nconst ATLAS_ROWS = {max(v['row'] for v in m.values()) + 1};\n")
    f.write(f"const ATLAS_MAP = {json.dumps(m)};\n")
```

---

## Chunk 2: Three.js Voxel Renderer

Core 3D rendering: scene, camera, merged voxel geometry with correct textures and face culling.

### Task 2: Create the 3D viewer template

**Files:**
- Create: `plugins/minecraft-prism-client/skills/redstone/assets/viewer-template-3d.html`

This is a NEW file (not modifying the 2D template). The skill's SKILL.md will be updated later to reference it.

- [ ] **Step 1: Write the HTML shell with Three.js importmap**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}} — Redstone 3D Viewer</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #1a1a2e; color: #e0e0e0; font-family: system-ui, sans-serif; overflow: hidden; }
  #canvas { width: 100vw; height: 100vh; display: block; }
  #ui { position: absolute; top: 16px; left: 16px; z-index: 10; }
  #ui h1 { font-size: 1.4rem; margin-bottom: 4px; }
  #ui .subtitle { color: #8a8a9a; font-size: 0.85rem; margin-bottom: 12px; }
  #controls {
    position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: rgba(22,33,62,0.9); border: 1px solid #2a2a4a;
    border-radius: 8px; padding: 12px 20px; z-index: 10;
    display: flex; align-items: center; gap: 16px;
  }
  #controls label { font-size: 0.85rem; color: #8a8a9a; }
  #controls input[type=range] { width: 200px; }
  #controls .y-val { font-weight: 600; min-width: 40px; }
  #materials {
    position: absolute; top: 16px; right: 16px; z-index: 10;
    background: rgba(22,33,62,0.9); border: 1px solid #2a2a4a;
    border-radius: 8px; padding: 12px; max-height: 80vh; overflow-y: auto;
    font-size: 0.8rem;
  }
</style>
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.170.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.170.0/examples/jsm/"
  }
}
</script>
</head>
<body>
<canvas id="canvas"></canvas>
<div id="ui">
  <h1>{{TITLE}}</h1>
  <p class="subtitle">{{DESCRIPTION}}</p>
</div>
<div id="controls">
  <label>Cross-section Y:</label>
  <input type="range" id="ySlider" min="0" max="10" value="10" step="1">
  <span class="y-val" id="yVal">All</span>
</div>
<div id="materials"></div>

<script type="module">
// === DATA (filled by skill agent) ===
const BUILD_DATA = {{BUILD_DATA_JSON}};
const BLOCKS = { /* same block definitions as 2D template */ };
const FACE_MAP = { /* same face map as 2D template */ };

// Atlas texture + UV map will be embedded here
// const ATLAS_DATA = 'data:image/png;base64,...';
// const ATLAS_MAP = {...};
// const ATLAS_COLS = 16;
// const ATLAS_ROWS = 13;

// === THREE.JS SETUP ===
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ... (see subsequent steps)
</script>
</body>
</html>
```

- [ ] **Step 2: Implement VoxelWorld class**

Inside the `<script type="module">` block. This class converts BUILD_DATA into merged Three.js geometry with face culling and correct UV mapping from the texture atlas.

Key methods:
- `constructor(buildData, atlasMap)` — parses layers into a 3D voxel array
- `getVoxel(x, y, z)` — returns block info at position
- `generateGeometry()` — iterates all voxels, checks 6 neighbors, emits faces only where no neighbor exists. Computes UV coordinates from `ATLAS_MAP` and `FACE_MAP` to show the correct face texture.

Face texture selection (same logic as 2D viewer):
- For each face direction (up/down/north/south/east/west), look up the block in FACE_MAP
- Up face → `faces.top`, Down face → `faces.bottom`, Side faces → `faces.side`
- Blocks with `front`/`back` (observer, dispenser): north face = front, south face = back
- Fall back to block ID if no FACE_MAP entry

Returns a `THREE.BufferGeometry` with position, normal, and uv attributes.

- [ ] **Step 3: Implement scene setup**

```javascript
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

// Orthographic camera (BlueMap-style default)
const aspect = window.innerWidth / window.innerHeight;
const frustum = 12;
const camera = new THREE.OrthographicCamera(
  -frustum * aspect, frustum * aspect, frustum, -frustum, 0.1, 100
);
// Isometric-ish angle
camera.position.set(15, 15, 15);
camera.lookAt(0, 0, 0);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(5, 10, 5);
scene.add(dirLight);
```

- [ ] **Step 4: Load atlas texture and create material**

```javascript
const textureLoader = new THREE.TextureLoader();
const atlasTexture = textureLoader.load(ATLAS_DATA);
atlasTexture.magFilter = THREE.NearestFilter;
atlasTexture.minFilter = THREE.NearestFilter;
atlasTexture.colorSpace = THREE.SRGBColorSpace;

// Clipping plane for cross-section
const clipPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 10);

const material = new THREE.MeshLambertMaterial({
  map: atlasTexture,
  clippingPlanes: [clipPlane],
  side: THREE.FrontSide,
});
```

- [ ] **Step 5: Build and add voxel mesh**

```javascript
const world = new VoxelWorld(BUILD_DATA, ATLAS_MAP, ATLAS_COLS, ATLAS_ROWS);
const geometry = world.generateGeometry();
const mesh = new THREE.Mesh(geometry, material);

// Center the build at origin
const layers = BUILD_DATA.layers;
const width = layers[0].grid[0].length;
const depth = layers[0].grid.length;
const height = layers.length;
mesh.position.set(-width / 2, 0, -depth / 2);

scene.add(mesh);
```

- [ ] **Step 6: Implement Y-slider cross-section**

```javascript
const ySlider = document.getElementById('ySlider');
const yVal = document.getElementById('yVal');
const minY = layers[0].y;
const maxY = layers[layers.length - 1].y;
ySlider.min = minY;
ySlider.max = maxY + 1; // +1 = show all
ySlider.value = maxY + 1;

ySlider.addEventListener('input', () => {
  const v = parseInt(ySlider.value);
  if (v > maxY) {
    yVal.textContent = 'All';
    clipPlane.constant = maxY + 2; // above everything
  } else {
    yVal.textContent = `Y=${v}`;
    clipPlane.constant = v - minY + 1; // clip above this layer
  }
});
```

- [ ] **Step 7: Render loop + resize**

```javascript
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  const a = window.innerWidth / window.innerHeight;
  camera.left = -frustum * a;
  camera.right = frustum * a;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

- [ ] **Step 8: Commit**

```bash
git add plugins/minecraft-prism-client/skills/redstone/assets/viewer-template-3d.html
git commit -m "feat: add Three.js 3D voxel viewer template"
```

---

## Chunk 3: Test & Deploy

### Task 3: Generate test build and deploy to VPS

- [ ] **Step 1: Build test HTML from template**

Use `sed` to replace placeholders with a test build (e.g., the same piston/observer/dispenser test data from the rotation tests) and generate a file at `/tmp/3d-test.html`.

- [ ] **Step 2: Upload to VPS**

```bash
scp /tmp/3d-test.html dev:/home/dev/redstone-viewer/3d-test.html
```

- [ ] **Step 3: Verify with Playwright screenshots**

Take screenshots at default angle, rotated, and with Y-slider at different positions.

- [ ] **Step 4: Iterate on visual issues**

Fix any texture mapping, camera angle, or lighting issues based on screenshots.

---

## Chunk 4: Materials panel + hover tooltips

### Task 4: Add UI overlays

- [ ] **Step 1: Materials list**

Render `BUILD_DATA.materials` in the `#materials` panel (same as 2D viewer but floating overlay).

- [ ] **Step 2: Raycasting for hover tooltips**

Use Three.js raycasting on mouse move to detect which voxel the cursor is over. Show block name + direction in a floating tooltip div.

- [ ] **Step 3: Commit**

```bash
git add plugins/minecraft-prism-client/skills/redstone/assets/viewer-template-3d.html
git commit -m "feat: add materials panel and hover tooltips to 3D viewer"
```

---

## Open Questions

1. **Keep 2D template too?** Probably yes — 2D is lighter weight and works on low-end devices. The skill agent can choose which template to use.
2. **Atlas size**: 201 textures at 16x16 in a 16-column grid = 256x208 pixels. Tiny. Could go 32x32 for better quality at close zoom.
3. **Block direction in 3D**: In 3D, block direction means actual face rotation of the mesh. Pistons facing east have their head on the +X face. This is more natural than the 2D workarounds — each face just gets the correct texture from FACE_MAP.
