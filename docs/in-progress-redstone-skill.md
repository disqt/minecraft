# In-Progress: Redstone Skill & Viewer Template

## What It Is

A Claude Code skill (`plugins/minecraft-prism-client/skills/redstone/`) that helps beginners design, understand, and build redstone circuits. The skill generates self-contained HTML viewer files with layer-by-layer build guides.

## VPS Serving

- **URL**: `https://disqt.com/minecraft/redstone/<filename>.html`
- **Nginx config**: `location /minecraft/redstone/` → `alias /home/dev/redstone-viewer/`
- **Upload**: `scp <file> dev:/home/dev/redstone-viewer/<filename>.html` (uses `dev` SSH user, NOT `minecraft`)
- The `minecraft` SSH user has no `www` directory

## Viewer Template Architecture

File: `plugins/minecraft-prism-client/skills/redstone/assets/viewer-template.html` (~95KB)

### Textures
- 201 base64-encoded textures from PrismarineJS/minecraft-assets (MIT license)
- Source: `cdn.jsdelivr.net/gh/PrismarineJS/minecraft-assets@master/data/1.21.4/blocks/`
- Scrape script at `/tmp/mc-textures/scrape_all.py` (curated list, not all 1088 blocks)
- Embedded as `const BLOCK_TEXTURES = {...}` data URIs, ~71KB
- CSS `image-rendering: pixelated` for crisp 16x16→48x48 upscaling

### Face-Aware Rendering with FACE_MAP
Each directional block has a FACE_MAP entry with explicit keys:
- `top`: texture shown when block faces UP (what viewer sees looking down)
- `bottom`: texture shown when block faces DOWN
- `nsew`: texture used for NSEW directions (rotated by DIRECTION_ROTATION)
- `nsewRotate: false`: opt-out of rotation (block shows same texture for all NSEW, arrow indicates direction)
- `side`, `front`, `back`: available for side view and future use

Per-block rendering strategy (user-validated):
- **Pistons**: `nsew: 'piston_side'` — side texture rotated, head points in correct direction
- **Observers**: `nsew: 'observer_top'` — asymmetric top texture rotated. `top: 'observer_front'` (eyes face at viewer when facing up). `bottom: 'observer_back'` (output side visible when facing down)
- **Dispensers/Droppers**: `nsew: 'furnace_top'` — plain stone top (physically correct from above). `top: 'dispenser_front_vertical'` (hole visible when facing up). `bottom: 'furnace_top'`
- **Furnace**: `nsew: 'furnace_top'`, `nsewRotate: false`
- **Flat blocks** (repeaters, comparators): no FACE_MAP, top texture rotated by direction

### Directional Texture Rotation
- `DIRECTION_ROTATION = { north: 0, south: 180, east: 90, west: 270 }`
- `blockStyle(blockId, direction)` returns `{ bg, rot }` — CSS background + rotation degrees
- Texture rendered in a `.block-tex` child div (position:absolute, inset:0) rotated independently of labels/tooltips
- `nsewRotate: false` in FACE_MAP opts out of rotation (arrow-only direction)

### View Modes (implemented this session)
- **Top-down view**: Layer-by-layer, one layer at a time. Layer selector buttons. Ghost layer toggle.
- **Side view**: Vertical cross-section at a given Z row. All layers stacked (highest Y at top). Z-slice selector buttons.
- Toggle between views with Top-down / Side view buttons
- `setView('top')` / `setView('side')` switches mode and rebuilds nav
- Side view uses `blockStyleSide()` — shows `faces.side` texture, no rotation
- Prev/Next buttons and arrow keys work for both modes

### Labels
- Hidden by default, shown on hover (CSS `opacity: 0` → `opacity: 1` on `.cell:hover`)
- Text shadow for readability over textures

### Template Placeholders
`{{TITLE}}`, `{{DESCRIPTION}}`, `{{WIDTH}}`, `{{DEPTH}}`, `{{HEIGHT}}`, `{{TOTAL_BLOCKS}}`, `{{DIFFICULTY}}`, `{{EXPLANATION}}`, `{{BUILD_DATA_JSON}}`

### BUILD_DATA_JSON Structure
```json
{
  "materials": { "block_id": count, ... },
  "layers": [
    {
      "y": 1,
      "note": "optional layer description",
      "grid": [
        ["block_id:direction", null, "block_id", ...],
        ...
      ]
    }
  ]
}
```
Direction format: `block_id:north`, `block_id:east`, etc. Null = empty cell.

## What's Done
- [x] 201 textures scraped and embedded
- [x] Face-aware rendering (FACE_MAP + getTextureKey) — all blocks user-validated
- [x] Hover-only labels
- [x] Directional texture rotation (.block-tex child div approach)
- [x] Ghost layer (shows previous layer faintly)
- [x] Side view (vertical cross-sections by Z row)
- [x] View mode toggle (Top-down / Side view)
- [x] Rotation test uploaded to VPS and validated via Playwright screenshots

## 3D Viewer (Three.js) — NEW

File: `plugins/minecraft-prism-client/skills/redstone/assets/viewer-template-3d.html` (~120KB)
Design doc: `docs/plans/2026-03-10-3d-voxel-viewer.md`

### Architecture
- Three.js r170 loaded via CDN `<script type="importmap">` (unpkg)
- OrthographicCamera for BlueMap-style isometric default view
- OrbitControls for drag-to-orbit, scroll-to-zoom
- Merged geometry with face culling (Three.js official voxel approach)
- Same `BUILD_DATA_JSON` / `BLOCKS` / `FACE_MAP` as 2D template

### Texture Atlas
- 201 PrismarineJS textures combined into one 256x208px atlas PNG
- Atlas builder: `/tmp/mc-textures/build-atlas.py` (Pillow required)
- Outputs: `atlas.png`, `atlas-map.json`, `atlas-data.js` (base64), `atlas-uv-map.js`
- UV coords computed from `ATLAS_MAP[textureName]` → `{col, row}` with `ATLAS_COLS=16, ATLAS_ROWS=13`

### Cross-Section (tri-axis dual-range)
- No clipping planes — geometry is rebuilt on slider change for correct internal face exposure
- `buildGeometry(buildInfo, clipBounds)` accepts `{ xMin, xMax, yMin, yMax, zMin, zMax }`
- Voxels outside clip bounds are skipped; neighbors outside bounds are treated as absent (shared faces generated)
- 3 dual-range sliders (X red, Y green, Z blue), each with min/max thumbs for bi-directional cropping
- Click-on-track jumps nearest thumb; double-click resets axis to "All"
- Floating layer note for Y-axis cross-sections

### Face Texture Selection in 3D (FACE_MAP_3D)
The 2D `FACE_MAP` uses viewport semantics (top = "what you see looking down"). The 3D viewer uses `FACE_MAP_3D` with physical semantics:
- `front`: the "business end" (piston push face, observer eyes, dispenser mouth)
- `back`: opposite of front
- `top`/`bottom`/`side`: geometric faces
- `all`: single texture on every face (for redstone_dust, water, etc.)
- The resolver `resolve3DTexture(block, blockDir, worldFace)` returns `{ tex, uvRot }` — texture name + UV rotation

### UV Rotation System (critical for directional blocks)
The Three.js voxel face corners map texture V differently per face:
- East/West: texture V axis → world Y (vertical) ✓
- North/South: texture V axis → world X (rotated 90°!) ✗
- This is invisible for symmetric textures (stone) but breaks directional textures (piston_side)

**Three independent rotation systems (all computed algorithmically from face corners):**
1. `TOP_UV_ROT` — rotates UP face textures for NSEW blocks (e.g., observer_top arrow)
   - `{ north: 1, south: 3, east: 2, west: 0 }`
   - At uvRot=0, UP face arrow points WEST (90° offset from Minecraft's base UV)
2. `BOTTOM_UV_ROT` — rotates DOWN face textures (different base UV than UP)
   - `{ north: 1, south: 3, east: 0, west: 2 }`
   - At uvRot=0, DOWN face arrow points EAST
3. `SIDE_UV_ROT` — rotates side textures for `SIDE_ROTATE_BLOCKS` (piston arm grain alignment)
   - Full 24-entry lookup table: `SIDE_UV_ROT[blockDir][worldFace]`
   - Key values for piston facing UP: `{ north: 1, south: 1, east: 0, west: 0 }`

**Critical**: ALL UV rotation tables MUST be computed algorithmically from Three.js face corner positions (maximize dot product of V=1 corners with target direction). Never manually set from Minecraft blockstate Y-rotation values — our renderer has different base UV orientations per face.
- Verification/computation script: `/tmp/verify-uv-rotations.js` (SIDE), `/tmp/verify-top-uv-rotations.js` (TOP/BOTTOM)

**Resolver logic (order of precedence):**
1. Front face (worldFace === blockDir): front texture, no rotation
2. Back face (worldFace === opposite): back texture, no rotation
3. Specific top/bottom texture exists: use with TOP_UV_ROT
4. Fallback to side texture: use with SIDE_UV_ROT (for SIDE_ROTATE_BLOCKS only)

`uvSets[0..3]` provides 4 pre-computed UV corner arrays for 0°/90°/180°/270° CW rotation.

### Geometry (official Three.js voxel pattern)
- Face corners use Three.js official ordering: [top-left, bottom-left, top-right, bottom-right] per face
- Index pattern: `ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3` (CCW winding)
- **Critical**: the original code had CW winding (reversed), causing visible back-faces. Headless Playwright screenshots didn't catch this because SwiftShader doesn't properly cull back-faces — only visible in a real browser.

### Flat blocks
- Blocks in `FLAT_BLOCKS` set (redstone_dust, rails, repeaters, etc.) render as thin slabs (1/16 height, top face only)
- Flat blocks are excluded from neighbor culling checks so the block below retains its top face

### Cross-Section UX Research (2026-03-11)
Evaluated 3 approaches for tri-axis bi-directional cross-sections:
- **A: Dual-range sliders** (chosen) — 2 thumbs per axis, visual fill bar, click-to-jump, dbl-click reset
- **B: Litematica mode selector** — 5 modes (All/Single/Range/Above/Below), precise but one axis at a time
- **C: Stepper bars** — arrow buttons per axis, precise but slow for large ranges
- Mockup deployed: `https://disqt.com/minecraft/redstone/cross-section-ux.html`
- Research sources: Litematica (LayerMode.java, LayerRange.java), Three.js clipping examples, Cornerstone.js MPR

### Assembly Process
Template assembled via `cat` from parts (since it's too large for Write tool):
- Source parts stored in `/tmp/3d-new-head.html`, `/tmp/3d-new-facemap.js`, `/tmp/3d-new-code.js`
- Data sections extracted from `/tmp/3d-test-v5.html` lines 216-296 (BUILD_DATA, BLOCKS, BLOCK_TEXTURES) and 345-348 (ATLAS data)
- Concatenated: `cat head.html + data(216-296) + facemap.js + atlas(345-348) + code.js > 3d-test-vN.html`
- **Always grep for stray `</content>` and `</invoke>` XML tags after assembly** (Write tool artifact)

### Status
- [x] Atlas builder working (201 textures, 95KB base64)
- [x] Three.js renderer working — textured blocks, isometric camera, orbit controls
- [x] Face winding fixed (CCW, matches Three.js official voxel example)
- [x] FACE_MAP_3D with proper front/back/top/side directional mapping
- [x] Flat block rendering (thin slabs, transparent via alphaTest)
- [x] Tri-axis dual-range cross-section (X/Y/Z, both directions per axis)
- [x] Geometry rebuild on cross-section change (correct internal face exposure)
- [x] Materials panel with texture swatches
- [x] Raycasting hover tooltips
- [x] Polished UI: Silkscreen pixel font, IBM Plex Mono, CSS variables, color-coded sliders
- [x] TOP_UV_ROT for directional top textures (observer_top arrow) — fixed from Minecraft values to algorithmic
- [x] BOTTOM_UV_ROT for directional bottom textures (separate from TOP — different base UV)
- [x] SIDE_UV_ROT lookup table for directional side textures (piston arm grain)
- [x] Test deployed to VPS: `https://disqt.com/minecraft/redstone/3d-test.html` (v9)
- [x] Verified via Playwright screenshots (note: headless can't catch winding/UV bugs)
- [x] Unit test suite: `redstone-viewer/tests/test-3d-texture-resolver.js` (413 tests)

### What Remains for 3D
- [ ] Verify all UV fixes in real browser (v9 deployed — observer arrow fix, user hasn't tested yet)
- [ ] Mobile touch support (orbit controls should work but needs testing)
- [ ] Redstone dust tinting (texture is gray, Minecraft tints it red — needs vertex coloring)
- [ ] Merge working code back into the template (`viewer-template-3d.html`)

## What Remains (Overall)
- [ ] Run skill-creator eval test cases (3 test prompts)
- [ ] Grade test results and launch eval viewer
- [ ] Update SKILL.md to instruct agents to scp generated viewers to VPS
- [ ] Update SKILL.md to reference both 2D and 3D templates
- [ ] Add pre-built hidden entrance design to circuit-catalog.md
- [ ] Iterate on skill based on eval feedback

## Key Gotchas
- **Face winding order**: Three.js uses CCW for front-facing. The original code had CW corners → back-faces visible, front-faces culled. Fix: adopt the official Three.js voxel face corners + index pattern `ndx, ndx+1, ndx+2, ndx+2, ndx+1, ndx+3`.
- **Headless Playwright can't catch winding bugs**: SwiftShader (Chromium's software WebGL) doesn't properly cull back-faces. Screenshots look fine but real browsers show inside-out geometry. Always test in a real browser for WebGL rendering issues.
- **Atlas texture names vs block IDs**: Some blocks (redstone_dust, piston, observer, dispenser) have no direct atlas entry matching their block ID. Must map via FACE_MAP_3D to actual atlas texture names (e.g., redstone_dust → redstone_dust_dot).
- **Flat blocks and neighbor culling**: If a flat block (dust, rails) occupies a voxel space, the solid block below has its top face culled (neighbor exists). Fix: exclude flat blocks from neighbor opacity checks.
- **Stray XML tags**: When using the Write tool to create HTML template parts for cat-concatenation, `</content>` and `</invoke>` XML tags from the tool response got embedded in the file. Fix: always verify assembled output.
- **SCP to VPS**: Use `dev` user, path `/home/dev/redstone-viewer/`, NOT `minecraft` user.
- **ES module imports**: When assembling the 3D template via `cat`, all `const` definitions and `import` statements end up in one `<script type="module">`. All referenced constants (BLOCKS, FACE_MAP_3D, ATLAS_MAP etc.) must be in the same module scope.
- **Pillow required**: `pip3 install --break-system-packages Pillow` on Raspberry Pi for atlas building.
- **Three.js face UV orientation mismatch**: East/West faces map texture V to world Y (correct), but North/South faces map texture V to world X (rotated 90°). Invisible for symmetric textures, breaks directional ones (piston_side). Fix: `SIDE_UV_ROT[blockDir][worldFace]` lookup table.
- **Don't apply same UV rotation to all 4 side faces**: E/W and N/S have different inherent UV orientations. Applying one rotation to all 4 fixes 2 faces but breaks the other 2.
- **Don't copy Minecraft blockstate Y-rotation values for UV tables**: Our Three.js face corners have different base UV orientations than Minecraft's model system. The UP face has a 90° offset, DOWN face has a different offset again. Always compute UV rotations algorithmically from the actual face corner positions.
- **UP and DOWN faces need separate UV rotation tables**: The base UV orientation differs (UP: arrow→West at rot 0, DOWN: arrow→East at rot 0). Using the same table for both produces wrong results on one of them.
- **Geometry rebuild vs clipping planes for cross-sections**: Clipping planes hide geometry at render time but can't reveal internal faces that were never generated (neighbor-culled at build time). Fix: rebuild geometry when cross-section changes, treating clipped neighbors as absent.
- **Playwright node path**: `NODE_PATH=/home/leo/.npm/_npx/e41f203b7505f1fb/node_modules` required to find playwright module from any working directory.
