# scripts/migrate_regions.py
"""Parse Minecraft .mca region file headers to count existing chunks."""

import struct
from pathlib import Path

from migrate_nbt import extract_chunk_tags

HEADER_ENTRIES = 1024
ENTRY_SIZE = 4  # bytes per location entry
HEADER_SIZE = HEADER_ENTRIES * ENTRY_SIZE  # 4096 bytes
SECTOR_SIZE = 4096


def count_chunks_in_region(region_path: Path) -> int:
    """Count non-empty chunks in a single .mca file by reading its location header.

    Each region file starts with 1024 4-byte location entries.
    A non-zero entry means the chunk exists.
    """
    with region_path.open("rb") as f:
        data = f.read(HEADER_SIZE)
    if len(data) < HEADER_SIZE:
        return 0
    count = 0
    for i in range(HEADER_ENTRIES):
        offset = i * ENTRY_SIZE
        entry = struct.unpack_from(">I", data, offset)[0]
        if entry != 0:
            count += 1
    return count


def count_chunks_in_directory(region_dir: Path) -> int:
    """Count all existing chunks across all .mca files in a region directory."""
    if not region_dir.is_dir():
        return 0
    total = 0
    for mca_file in sorted(region_dir.glob("r.*.*.mca")):
        total += count_chunks_in_region(mca_file)
    return total


def analyze_region(region_path: Path, threshold: int) -> dict:
    """Read a single .mca file and extract InhabitedTime from each chunk's NBT data.

    Returns a dict mapping (chunk_x, chunk_z) to:
        {"inhabited_time": int, "data_version": int, "delete": bool}

    A chunk is marked for deletion when its InhabitedTime is below the threshold.
    """
    data = region_path.read_bytes()
    if len(data) < 8192:
        return {}
    results = {}
    # Parse region coords from filename: r.X.Z.mca
    parts = region_path.stem.split(".")
    region_x, region_z = int(parts[1]), int(parts[2])

    for i in range(HEADER_ENTRIES):
        loc_offset = i * ENTRY_SIZE
        entry = struct.unpack_from(">I", data, loc_offset)[0]
        if entry == 0:
            continue
        sector_offset = (entry >> 8) * SECTOR_SIZE
        if sector_offset + 5 > len(data):
            continue
        chunk_len = struct.unpack_from(">I", data, sector_offset)[0]
        compression = data[sector_offset + 4]
        compressed_start = sector_offset + 5
        compressed_end = sector_offset + 4 + chunk_len
        if compressed_end > len(data):
            continue
        compressed_data = data[compressed_start:compressed_end]
        tags = extract_chunk_tags(compressed_data, compression)
        inhabited = tags["InhabitedTime"] if tags.get("InhabitedTime") is not None else 0
        dv = tags["DataVersion"] if tags.get("DataVersion") is not None else 0
        local_x = i % 32
        local_z = i // 32
        chunk_x = region_x * 32 + local_x
        chunk_z = region_z * 32 + local_z
        results[(chunk_x, chunk_z)] = {
            "inhabited_time": inhabited,
            "data_version": dv,
            "delete": inhabited < threshold,
        }
    return results


def analyze_dimension(region_dir: Path, threshold: int) -> tuple[dict, dict]:
    """Scan all .mca files in a region directory and analyze each chunk.

    Returns (stats_dict, grid_dict) where:
        stats_dict: {"total": int, "delete": int, "keep": int}
        grid_dict:  maps (chunk_x, chunk_z) to chunk analysis dicts (see analyze_region)
    """
    grid: dict = {}
    for mca_file in sorted(region_dir.glob("r.*.*.mca")):
        grid.update(analyze_region(mca_file, threshold))
    total = len(grid)
    delete_count = sum(1 for v in grid.values() if v["delete"])
    stats = {"total": total, "delete": delete_count, "keep": total - delete_count}
    return stats, grid
