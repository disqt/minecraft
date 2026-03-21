"""HTML preview generator — self-contained migration preview page.

Produces a single HTML file with a canvas grid (green=keep, red=delete,
dark=unexplored), dimension tabs, stats bar, and embedded chunk data.

Chunk data is packed as Uint8 per chunk:
  bit 7 = exists (1) or unexplored (0)
  bit 6 = delete flag (1=delete, 0=keep)
  bits 0-5 = inhabited_bucket value (0-5)
"""

import base64
import struct
from datetime import datetime
from pathlib import Path
from typing import Any

from migrate_nbt import inhabited_bucket

# ---------------------------------------------------------------------------
# Colour constants (kept in sync with the JS template below)
# ---------------------------------------------------------------------------
_COLOR_BG = "#1a1a2e"
_COLOR_KEEP = "#2d8a4e"
_COLOR_DELETE = "#c0392b"
_COLOR_UNEXPLORED = "#2a2a3e"
_COLOR_BORDER = "#3a3a5e"

# Target canvas width for the grid area
_CANVAS_TARGET_PX = 800


def _pack_grid(grid: dict[tuple[int, int], dict]) -> tuple[bytes, int, int, int, int]:
    """Pack grid dict into a flat Uint8 array for embedding.

    Returns (data_bytes, min_x, min_z, width, height) where width × height
    covers the bounding box of all chunk coordinates.  Empty grids return
    (b'', 0, 0, 0, 0).
    """
    if not grid:
        return b"", 0, 0, 0, 0

    xs = [x for x, z in grid]
    zs = [z for x, z in grid]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    width = max_x - min_x + 1
    height = max_z - min_z + 1

    buf = bytearray(width * height)  # initialised to 0 (unexplored)

    for (cx, cz), info in grid.items():
        idx = (cz - min_z) * width + (cx - min_x)
        bucket = inhabited_bucket(info.get("inhabited_time") or 0)
        byte = 0x80  # bit 7: exists
        if info.get("delete"):
            byte |= 0x40  # bit 6: delete
        byte |= bucket & 0x3F  # bits 0-5
        buf[idx] = byte

    return bytes(buf), min_x, min_z, width, height


def _dim_label(dim_key: str) -> str:
    """Convert internal dimension key to display label."""
    mapping = {
        "overworld": "Overworld",
        "nether": "Nether",
        "end": "End",
        "the_end": "End",
    }
    return mapping.get(dim_key.lower(), dim_key.title())


def _build_dim_js_objects(dimensions: dict[str, dict]) -> str:
    """Build the JavaScript DIMS array literal embedded in the HTML."""
    parts: list[str] = []
    for dim_key, dim_data in dimensions.items():
        grid = dim_data.get("grid") or {}
        stats = dim_data.get("stats") or {"total": 0, "delete": 0, "keep": 0}
        packed, min_x, min_z, width, height = _pack_grid(grid)
        b64 = base64.b64encode(packed).decode("ascii")
        label = _dim_label(dim_key)
        total = stats.get("total", 0)
        delete = stats.get("delete", 0)
        keep = stats.get("keep", 0)
        pct = (delete / total * 100) if total > 0 else 0.0
        parts.append(
            f"""{{
      key: {_js_str(dim_key)},
      label: {_js_str(label)},
      stats: {{total: {total}, delete: {delete}, keep: {keep}, pct: {pct:.1f}}},
      grid: {{minX: {min_x}, minZ: {min_z}, width: {width}, height: {height}}},
      data: "{b64}"
    }}"""
        )
    return "[\n    " + ",\n    ".join(parts) + "\n  ]"


def _js_str(s: str) -> str:
    """Wrap a Python string as a JS string literal (double-quoted, basic escaping)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chunk Migration Preview</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: {bg};
    color: #e0e0f0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px;
    padding: 16px;
  }}
  h1 {{ font-size: 16px; margin-bottom: 4px; color: #a0a0d0; letter-spacing: 1px; }}
  .meta {{ color: #606080; margin-bottom: 12px; font-size: 12px; }}
  /* Tabs */
  .tabs {{ display: flex; gap: 4px; margin-bottom: 8px; }}
  .tab {{
    padding: 4px 14px;
    background: #252540;
    border: 1px solid #3a3a5e;
    border-radius: 3px 3px 0 0;
    cursor: pointer;
    color: #8080b0;
    transition: background 0.15s;
  }}
  .tab.active {{ background: #2a2a50; color: #d0d0ff; border-bottom-color: #2a2a50; }}
  .tab:hover:not(.active) {{ background: #2a2a44; }}
  /* Stats bar */
  .stats-bar {{
    background: #252540;
    border: 1px solid #3a3a5e;
    border-radius: 3px;
    padding: 8px 12px;
    margin-bottom: 10px;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }}
  .stat {{ display: flex; flex-direction: column; }}
  .stat-label {{ color: #606080; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
  .stat-value {{ font-size: 15px; font-weight: bold; }}
  .stat-value.keep {{ color: {keep}; }}
  .stat-value.delete {{ color: {delete}; }}
  .stat-value.pct {{ color: #c0a030; }}
  /* Canvas panel */
  .canvas-panel {{
    background: #252540;
    border: 1px solid #3a3a5e;
    border-radius: 3px;
    padding: 8px;
    display: inline-block;
  }}
  canvas {{ display: block; image-rendering: pixelated; }}
  /* Legend */
  .legend {{
    margin-top: 10px;
    display: flex;
    gap: 16px;
    align-items: center;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; font-size: 11px; color: #8080a0; }}
  .swatch {{ width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }}
</style>
</head>
<body>
<h1>Chunk Migration Preview</h1>
<div class="meta">
  Query: <span style="color:#c0c070">{query}</span>
  &nbsp;&middot;&nbsp;
  Generated: <span style="color:#7070a0">{timestamp}</span>
</div>

<div class="tabs" id="tabs"></div>
<div class="stats-bar" id="stats-bar"></div>
<div class="canvas-panel"><canvas id="grid-canvas"></canvas></div>
<div class="legend">
  <div class="legend-item"><div class="swatch" style="background:{keep}"></div> Keep</div>
  <div class="legend-item"><div class="swatch" style="background:{delete}"></div> Delete</div>
  <div class="legend-item"><div class="swatch" style="background:{unexplored}"></div> Unexplored</div>
</div>

<script>
const DIMS = {dims_js};

// Colour constants
const C_KEEP       = "{keep}";
const C_DELETE     = "{delete}";
const C_UNEXPLORED = "{unexplored}";
const C_BORDER     = "{border}";
const CANVAS_TARGET = {canvas_target};

let activeDim = 0;

function b64ToBytes(b64) {{
  const bin = atob(b64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return arr;
}}

function renderDim(idx) {{
  activeDim = idx;
  const dim = DIMS[idx];

  // Update tab highlights
  document.querySelectorAll('.tab').forEach((el, i) => {{
    el.classList.toggle('active', i === idx);
  }});

  // Update stats bar
  const s = dim.stats;
  document.getElementById('stats-bar').innerHTML = `
    <div class="stat">
      <span class="stat-label">Total</span>
      <span class="stat-value">${{s.total.toLocaleString()}}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Keep</span>
      <span class="stat-value keep">${{s.keep.toLocaleString()}}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Delete</span>
      <span class="stat-value delete">${{s.delete.toLocaleString()}}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Delete %</span>
      <span class="stat-value pct">${{s.pct.toFixed(1)}}%</span>
    </div>
  `;

  // Draw canvas
  const g = dim.grid;
  const canvas = document.getElementById('grid-canvas');
  if (g.width === 0 || g.height === 0) {{
    canvas.width = CANVAS_TARGET;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = C_UNEXPLORED;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#606080';
    ctx.font = '13px monospace';
    ctx.fillText('(no chunks)', 12, 40);
    return;
  }}

  const cellSize = Math.max(1, Math.floor(CANVAS_TARGET / Math.max(g.width, g.height)));
  const cw = g.width * cellSize;
  const ch = g.height * cellSize;
  canvas.width = cw;
  canvas.height = ch;

  const ctx = canvas.getContext('2d');
  ctx.fillStyle = C_UNEXPLORED;
  ctx.fillRect(0, 0, cw, ch);

  const data = b64ToBytes(dim.data);
  for (let z = 0; z < g.height; z++) {{
    for (let x = 0; x < g.width; x++) {{
      const byte = data[z * g.width + x];
      if (!(byte & 0x80)) continue; // unexplored
      ctx.fillStyle = (byte & 0x40) ? C_DELETE : C_KEEP;
      ctx.fillRect(x * cellSize, z * cellSize, cellSize, cellSize);
    }}
  }}

  // Draw 1px grid lines if cells are large enough
  if (cellSize >= 4) {{
    ctx.strokeStyle = C_BORDER;
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= g.width; x++) {{
      ctx.beginPath(); ctx.moveTo(x * cellSize, 0); ctx.lineTo(x * cellSize, ch); ctx.stroke();
    }}
    for (let z = 0; z <= g.height; z++) {{
      ctx.beginPath(); ctx.moveTo(0, z * cellSize); ctx.lineTo(cw, z * cellSize); ctx.stroke();
    }}
  }}
}}

// Build tabs
const tabsEl = document.getElementById('tabs');
DIMS.forEach((dim, i) => {{
  const btn = document.createElement('button');
  btn.className = 'tab' + (i === 0 ? ' active' : '');
  btn.textContent = dim.label;
  btn.onclick = () => renderDim(i);
  tabsEl.appendChild(btn);
}});

// Initial render
renderDim(0);
</script>
</body>
</html>
"""


def generate_html(dimensions: dict[str, Any], query: str) -> str:
    """Generate a self-contained HTML preview string.

    Args:
        dimensions: Dict mapping dimension key -> {stats, grid}.
        query:      The query string used to select chunks for deletion.

    Returns:
        HTML string.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    dims_js = _build_dim_js_objects(dimensions)

    return _HTML_TEMPLATE.format(
        bg=_COLOR_BG,
        keep=_COLOR_KEEP,
        delete=_COLOR_DELETE,
        unexplored=_COLOR_UNEXPLORED,
        border=_COLOR_BORDER,
        canvas_target=_CANVAS_TARGET_PX,
        query=query.replace("<", "&lt;").replace(">", "&gt;"),
        timestamp=timestamp,
        dims_js=dims_js,
    )


def generate_html_file(
    dimensions: dict[str, Any],
    query: str,
    output_path: Path,
) -> None:
    """Write the HTML preview to a file.

    Args:
        dimensions:  Dict mapping dimension key -> {stats, grid}.
        query:       The query string used to select chunks for deletion.
        output_path: Destination file path (created or overwritten).
    """
    html = generate_html(dimensions, query)
    Path(output_path).write_text(html, encoding="utf-8")
