"""Generate binary overlay data files for the chunk inspector."""

import json
import struct
from datetime import datetime, timezone
from pathlib import Path

from migrate_nbt import inhabited_bucket


def _dimension_suffix(name: str) -> str:
    """Map a dimension name to its URL/file-safe suffix.

    Strips leading 'minecraft:' namespace prefix if present.
    """
    if ":" in name:
        name = name.split(":", 1)[1]
    return name.replace("/", "_")


def _encode_chunk(chunk: dict) -> int:
    """Encode a chunk dict to a single Uint8 byte.

    Bit layout:
      Bit 7: exists (always 1 for a present chunk)
      Bit 6: delete flag
      Bits 0-5: InhabitedTime bucket (0-5)
    """
    bucket = inhabited_bucket(chunk.get("inhabited_time", 0))
    byte = 0x80  # bit 7: exists
    if chunk.get("delete", False):
        byte |= 0x40  # bit 6: delete
    byte |= bucket & 0x3F  # bits 0-5
    return byte


def _write_dimension(
    dim_name: str,
    dim_data: dict,
    query: str,
    bin_path: Path,
    json_path: Path,
) -> None:
    """Write the binary file and JSON metadata for a single dimension."""
    grid = dim_data["grid"]
    stats = dim_data["stats"]

    if not grid:
        # Empty grid: write empty binary and minimal metadata
        bin_path.write_bytes(b"")
        meta = {
            "min_cx": 0,
            "max_cx": 0,
            "min_cz": 0,
            "max_cz": 0,
            "cols": 0,
            "rows": 0,
            "total": stats.get("total", 0),
            "delete": stats.get("delete", 0),
            "keep": stats.get("keep", 0),
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "dimension": dim_name,
        }
        json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return

    xs = [cx for cx, _cz in grid]
    zs = [cz for _cx, cz in grid]
    min_cx, max_cx = min(xs), max(xs)
    min_cz, max_cz = min(zs), max(zs)

    cols = max_cx - min_cx + 1
    rows = max_cz - min_cz + 1

    # Build flat Uint8 buffer, row-major: grid[z * cols + x]
    buf = bytearray(cols * rows)
    for (cx, cz), chunk in grid.items():
        x = cx - min_cx
        z = cz - min_cz
        buf[z * cols + x] = _encode_chunk(chunk)

    bin_path.write_bytes(bytes(buf))

    meta = {
        "min_cx": min_cx,
        "max_cx": max_cx,
        "min_cz": min_cz,
        "max_cz": max_cz,
        "cols": cols,
        "rows": rows,
        "total": stats.get("total", 0),
        "delete": stats.get("delete", 0),
        "keep": stats.get("keep", 0),
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dimension": dim_name,
    }
    json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def generate_raw_file(
    dimensions: dict,
    query: str,
    output_path: Path,
) -> None:
    """Generate binary overlay data file(s) and JSON metadata for the chunk inspector.

    Args:
        dimensions: Dict mapping dimension name -> {"stats": {...}, "grid": {...}}
                    where grid maps (chunk_x, chunk_z) -> chunk analysis dict.
        query:      Query string to embed in metadata (e.g. "InhabitedTime < 120").
        output_path: Desired output path.
                    - Single dimension: writes binary to output_path,
                      JSON metadata to <stem>.json alongside it.
                    - Multiple dimensions: writes <stem>-<dim>.bin and
                      <stem>-<dim>.json per dimension; output_path itself
                      is NOT created.
    """
    output_path = Path(output_path)
    stem = output_path.stem
    parent = output_path.parent

    dim_names = list(dimensions.keys())

    if len(dim_names) == 1:
        dim_name = dim_names[0]
        json_path = parent / (stem + ".json")
        _write_dimension(dim_name, dimensions[dim_name], query, output_path, json_path)
    else:
        for dim_name in dim_names:
            suffix = _dimension_suffix(dim_name)
            bin_path = parent / f"{stem}-{suffix}.bin"
            json_path = parent / f"{stem}-{suffix}.json"
            _write_dimension(dim_name, dimensions[dim_name], query, bin_path, json_path)
