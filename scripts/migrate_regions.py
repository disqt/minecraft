# scripts/migrate_regions.py
"""Parse Minecraft .mca region file headers to count existing chunks."""

import struct
from pathlib import Path

HEADER_ENTRIES = 1024
ENTRY_SIZE = 4  # bytes per location entry
HEADER_SIZE = HEADER_ENTRIES * ENTRY_SIZE  # 4096 bytes


def count_chunks_in_region(region_path: Path) -> int:
    """Count non-empty chunks in a single .mca file by reading its location header.

    Each region file starts with 1024 4-byte location entries.
    A non-zero entry means the chunk exists.
    """
    data = region_path.read_bytes()[:HEADER_SIZE]
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
