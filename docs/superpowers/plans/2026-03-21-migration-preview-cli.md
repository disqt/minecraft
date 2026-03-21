# Migration Preview CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI that analyzes Minecraft world chunks against a threshold/query, generates HTML preview reports and chunk inspector overlay data, and optionally trims matching chunks.

**Architecture:** Multi-module under `scripts/`. The CLI resolves a world (local or SSH), analyzes chunks via pure Python NBT parsing (for `--threshold`) or MCA Selector (for `--query`), then generates outputs: terminal stats, standalone HTML preview, and/or binary overlay for the chunk inspector. Optional destructive trim via `--dangerously-perform-the-trim`. Several modules already exist from a prior iteration and will be modified.

**Tech Stack:** Python 3.10+ stdlib (argparse, struct, zlib, pathlib, subprocess, base64, json, math), optional `lz4` pip package for MC 1.20.5+ chunks.

**Spec:** `docs/superpowers/specs/2026-03-21-migration-preview-cli-design.md`

---

## Existing Code

These files already exist and have passing tests from a prior iteration:

| File | Status | Notes |
|------|--------|-------|
| `scripts/migrate_regions.py` | **Keep, extend** | Has header parsing. Needs chunk NBT reading. |
| `scripts/migrate_display.py` | **Keep as-is** | Stats table + safety abort formatting. |
| `scripts/migrate_mca.py` | **Keep, update imports** | MCA Selector wrapper. Update `dimension_region_subpath` import (moved to new location). Fix exit code 3 -> 2. |
| `scripts/migrate_remote.py` | **Rewrite** | Needs PaperMC layout detection, progress. |
| `scripts/migrate.py` | **Rewrite** | Completely different arg parsing + pipeline. |
| `tests/test_migrate_regions.py` | **Keep, extend** | 4 tests passing. |
| `tests/test_migrate_display.py` | **Keep as-is** | 5 tests passing. |
| `tests/test_migrate_mca.py` | **Keep as-is** | 7 tests passing. |
| `tests/test_migrate_remote.py` | **Rewrite alongside module** | |
| `tests/test_migrate_args.py` | **Rewrite** | Old arg format. |
| `tests/conftest.py` | **Keep, extend** | Fixture generation. |

## File Structure

```
scripts/
  migrate.py            # CLI entry point — arg parsing, pipeline orchestration
  migrate_regions.py    # Region file parsing — headers, chunk NBT, InhabitedTime (MODIFY)
  migrate_nbt.py        # Minimal NBT tag reader — extract specific tags from compressed data (NEW)
  migrate_mca.py        # MCA Selector wrapper for --query mode (KEEP)
  migrate_remote.py     # World resolution — local layout detection, SSH download (REWRITE)
  migrate_display.py    # Terminal output — stats table, safety abort, report (KEEP)
  migrate_html.py       # Standalone HTML preview generator (NEW)
  migrate_raw.py        # Binary overlay output for chunk inspector (NEW)
tests/
  conftest.py           # Fixture generation (EXTEND with NBT fixtures)
  test_migrate_nbt.py   # NBT parsing tests (NEW)
  test_migrate_regions.py # Region + chunk analysis tests (EXTEND)
  test_migrate_remote.py  # Layout detection tests (REWRITE)
  test_migrate_args.py    # New CLI arg parsing tests (REWRITE)
  test_migrate_html.py    # HTML generation tests (NEW)
  test_migrate_raw.py     # Raw binary output tests (NEW)
  test_migrate_mca.py     # MCA Selector tests (KEEP)
  test_migrate_display.py # Display tests (KEEP)
  fixtures/
    r.0.0.mca           # Region with 5 chunks (EXISTS)
    r.0.1.mca           # Empty region (EXISTS)
    chunk_1_18.nbt       # Compressed chunk NBT, 1.18+ layout (NEW)
    chunk_pre_1_18.nbt   # Compressed chunk NBT, pre-1.18 layout (NEW)
```

---

## Task 1: Minimal NBT Tag Reader

The core new capability. Read `InhabitedTime` and `DataVersion` from compressed chunk NBT data without a full NBT parser. We only need to walk compound/list/string tags to find two specific named tags.

**Files:**
- Create: `scripts/migrate_nbt.py`
- Create: `tests/test_migrate_nbt.py`
- Modify: `tests/conftest.py` — add NBT fixture generation

- [ ] **Step 1: Create NBT test fixtures in conftest.py**

Add to `tests/conftest.py` — generate minimal compressed NBT data for testing. A chunk NBT is a compound tag containing `DataVersion` (int, tag ID 3) and `InhabitedTime` (long, tag ID 4). For 1.18+ these are at root level. For pre-1.18, `InhabitedTime` is under a `Level` compound.

```python
# Append to tests/conftest.py
import struct as _struct
import zlib as _zlib

def _build_nbt_compound(tags: dict, name: str = "") -> bytes:
    """Build a minimal NBT compound tag (tag ID 10).

    tags: {name: (tag_id, value_bytes)}
    """
    buf = bytearray()
    # Compound tag header: tag_id=10, name
    buf.append(10)
    buf.extend(_struct.pack(">H", len(name)))
    buf.extend(name.encode("utf-8"))
    for tag_name, (tag_id, value_bytes) in tags.items():
        buf.append(tag_id)
        buf.extend(_struct.pack(">H", len(tag_name)))
        buf.extend(tag_name.encode("utf-8"))
        buf.extend(value_bytes)
    buf.append(0)  # End tag
    return bytes(buf)

def _nbt_int(val: int) -> tuple[int, bytes]:
    return (3, _struct.pack(">i", val))

def _nbt_long(val: int) -> tuple[int, bytes]:
    return (4, _struct.pack(">q", val))

def _nbt_compound(tags: dict) -> tuple[int, bytes]:
    """Inner compound (no outer header — caller adds tag id + name)."""
    buf = bytearray()
    for tag_name, (tag_id, value_bytes) in tags.items():
        buf.append(tag_id)
        buf.extend(_struct.pack(">H", len(tag_name)))
        buf.extend(tag_name.encode("utf-8"))
        buf.extend(value_bytes)
    buf.append(0)  # End tag
    return (10, bytes(buf))

def pytest_configure(config):
    # ... existing fixture generation ...

    # chunk_1_18.nbt — zlib-compressed NBT, 1.18+ layout (root-level InhabitedTime)
    path_118 = FIXTURES / "chunk_1_18.nbt"
    if not path_118.exists():
        nbt = _build_nbt_compound({
            "DataVersion": _nbt_int(3955),
            "InhabitedTime": _nbt_long(500),
            "Status": (8, _struct.pack(">H", 4) + b"full"),  # string tag
        })
        path_118.write_bytes(_zlib.compress(nbt))

    # chunk_pre_1_18.nbt — zlib-compressed NBT, pre-1.18 layout (Level.InhabitedTime)
    path_pre = FIXTURES / "chunk_pre_1_18.nbt"
    if not path_pre.exists():
        nbt = _build_nbt_compound({
            "DataVersion": _nbt_int(2730),
            "Level": _nbt_compound({
                "InhabitedTime": _nbt_long(12000),
            }),
        })
        path_pre.write_bytes(_zlib.compress(nbt))
```

- [ ] **Step 2: Write failing tests for NBT extraction**

```python
# tests/test_migrate_nbt.py
import zlib
from pathlib import Path
from scripts.migrate_nbt import extract_chunk_tags

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_1_18_chunk():
    data = FIXTURES / "chunk_1_18.nbt"
    compressed = data.read_bytes()
    tags = extract_chunk_tags(compressed, compression=2)
    assert tags["DataVersion"] == 3955
    assert tags["InhabitedTime"] == 500


def test_extract_pre_1_18_chunk():
    data = FIXTURES / "chunk_pre_1_18.nbt"
    compressed = data.read_bytes()
    tags = extract_chunk_tags(compressed, compression=2)
    assert tags["DataVersion"] == 2730
    assert tags["InhabitedTime"] == 12000


def test_extract_handles_lz4_gracefully():
    """LZ4 chunks without lz4 installed should return None tags."""
    tags = extract_chunk_tags(b"\x00" * 100, compression=4)
    # Should return None values if lz4 not available, or parse if available
    assert tags is not None  # Never crashes
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_nbt.py -v`
Expected: FAIL — module not found

- [ ] **Step 4: Implement migrate_nbt.py**

```python
# scripts/migrate_nbt.py
"""Minimal NBT tag reader — extract specific tags from compressed chunk data.

Only reads enough of the NBT tree to find DataVersion and InhabitedTime.
Does not build a full NBT DOM. Supports zlib (type 2) and lz4 (type 4) compression.
"""

import struct
import sys
import zlib

# NBT tag type IDs
TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

# Size of fixed-width tags (for skipping)
_FIXED_SIZES = {
    TAG_BYTE: 1,
    TAG_SHORT: 2,
    TAG_INT: 4,
    TAG_LONG: 8,
    TAG_FLOAT: 4,
    TAG_DOUBLE: 8,
}


def _decompress(data: bytes, compression: int) -> bytes | None:
    """Decompress chunk data. Returns None if unsupported."""
    if compression == 2:
        return zlib.decompress(data)
    if compression == 1:
        import gzip
        return gzip.decompress(data)
    if compression == 4:
        try:
            import lz4.block
            # MC uses LZ4 block format with the uncompressed size prepended (4 bytes BE)
            uncompressed_size = struct.unpack(">I", data[:4])[0]
            return lz4.block.decompress(data[4:], uncompressed_size=uncompressed_size)
        except ImportError:
            return None
    if compression == 3:
        return data  # uncompressed
    return None


class _NBTReader:
    """Streaming NBT reader that extracts named tags without building a DOM."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def _read(self, n: int) -> bytes:
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def _read_string(self) -> str:
        length = struct.unpack(">H", self._read(2))[0]
        return self._read(length).decode("utf-8", errors="replace")

    def _skip_tag_payload(self, tag_type: int) -> None:
        """Skip over a tag's payload without reading it."""
        if tag_type in _FIXED_SIZES:
            self.pos += _FIXED_SIZES[tag_type]
        elif tag_type == TAG_STRING:
            length = struct.unpack(">H", self._read(2))[0]
            self.pos += length
        elif tag_type == TAG_BYTE_ARRAY:
            length = struct.unpack(">i", self._read(4))[0]
            self.pos += length
        elif tag_type == TAG_INT_ARRAY:
            length = struct.unpack(">i", self._read(4))[0]
            self.pos += length * 4
        elif tag_type == TAG_LONG_ARRAY:
            length = struct.unpack(">i", self._read(4))[0]
            self.pos += length * 8
        elif tag_type == TAG_LIST:
            item_type = struct.unpack(">b", self._read(1))[0]
            count = struct.unpack(">i", self._read(4))[0]
            for _ in range(count):
                self._skip_tag_payload(item_type)
        elif tag_type == TAG_COMPOUND:
            self._skip_compound()

    def _skip_compound(self) -> None:
        """Skip all tags in a compound until TAG_END."""
        while True:
            tag_type = struct.unpack(">b", self._read(1))[0]
            if tag_type == TAG_END:
                return
            self._read_string()  # tag name
            self._skip_tag_payload(tag_type)

    def extract_chunk_fields(self) -> dict:
        """Extract DataVersion and InhabitedTime from chunk NBT.

        Handles both 1.18+ (root level) and pre-1.18 (Level compound) layouts.
        Returns {"DataVersion": int|None, "InhabitedTime": int|None}.
        """
        result = {"DataVersion": None, "InhabitedTime": None}

        # Read root compound header
        tag_type = struct.unpack(">b", self._read(1))[0]
        if tag_type != TAG_COMPOUND:
            return result
        self._read_string()  # root name (usually empty)

        # Scan root compound tags
        while self.pos < len(self.data):
            tag_type = struct.unpack(">b", self._read(1))[0]
            if tag_type == TAG_END:
                break
            name = self._read_string()

            if name == "DataVersion" and tag_type == TAG_INT:
                result["DataVersion"] = struct.unpack(">i", self._read(4))[0]
                # If we have both, stop early
                if result["InhabitedTime"] is not None:
                    break
            elif name == "InhabitedTime" and tag_type == TAG_LONG:
                result["InhabitedTime"] = struct.unpack(">q", self._read(8))[0]
                if result["DataVersion"] is not None:
                    break
            elif name == "Level" and tag_type == TAG_COMPOUND:
                # Pre-1.18: InhabitedTime is inside Level compound
                result.update(self._scan_level_compound())
                if result["DataVersion"] is not None:
                    break
            else:
                self._skip_tag_payload(tag_type)

        return result

    def _scan_level_compound(self) -> dict:
        """Scan the Level compound for InhabitedTime."""
        result = {}
        while self.pos < len(self.data):
            tag_type = struct.unpack(">b", self._read(1))[0]
            if tag_type == TAG_END:
                break
            name = self._read_string()
            if name == "InhabitedTime" and tag_type == TAG_LONG:
                result["InhabitedTime"] = struct.unpack(">q", self._read(8))[0]
                # Found it — skip rest of Level
                self._skip_compound()
                break
            else:
                self._skip_tag_payload(tag_type)
        return result


def inhabited_bucket(ticks: int) -> int:
    """Map InhabitedTime ticks to a 0-5 bucket (logarithmic).

    Same scale as generate-chunk-data.py:
    0 = never, 1 = ~1-26 ticks, 2 = ~26-632, 3 = ~632-15.8K, 4 = ~15.8K-395K, 5 = 395K+
    """
    import math
    if ticks == 0:
        return 0
    return min(5, 1 + int(math.log10(max(1, ticks)) / math.log10(5000000) * 4))


def extract_chunk_tags(compressed_data: bytes, compression: int) -> dict:
    """Extract DataVersion and InhabitedTime from compressed chunk NBT.

    Args:
        compressed_data: Raw compressed bytes (after the 5-byte chunk header)
        compression: Compression type (1=gzip, 2=zlib, 3=none, 4=lz4)

    Returns:
        {"DataVersion": int|None, "InhabitedTime": int|None}
    """
    raw = _decompress(compressed_data, compression)
    if raw is None:
        return {"DataVersion": None, "InhabitedTime": None}
    try:
        reader = _NBTReader(raw)
        return reader.extract_chunk_fields()
    except (struct.error, IndexError):
        return {"DataVersion": None, "InhabitedTime": None}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_nbt.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/migrate_nbt.py tests/test_migrate_nbt.py tests/conftest.py
git commit -m "feat: minimal NBT reader for InhabitedTime and DataVersion extraction"
```

---

## Task 2: Extend Region Parser with Chunk Analysis

Add the ability to read individual chunk data from region files and extract per-chunk InhabitedTime/DataVersion using the NBT reader.

**Files:**
- Modify: `scripts/migrate_regions.py`
- Modify: `tests/test_migrate_regions.py`

- [ ] **Step 1: Write failing tests for chunk-level analysis**

```python
# Append to tests/test_migrate_regions.py
from scripts.migrate_regions import analyze_region, analyze_dimension


def make_region_with_chunks(path, chunks: list[dict]):
    """Build a .mca file with real chunk data at specific slots.

    Each chunk dict: {"slot": int (0-1023), "inhabited_time": int, "data_version": int}
    """
    import struct, zlib
    from tests.conftest import _build_nbt_compound, _nbt_int, _nbt_long

    header = bytearray(8192)  # location + timestamp tables
    sectors = bytearray()
    next_sector = 2  # sectors 0-1 are the header

    for chunk in chunks:
        slot = chunk["slot"]
        nbt = _build_nbt_compound({
            "DataVersion": _nbt_int(chunk["data_version"]),
            "InhabitedTime": _nbt_long(chunk["inhabited_time"]),
        })
        compressed = zlib.compress(nbt)
        # Chunk sector: 4 bytes length + 1 byte compression type + data
        chunk_data = struct.pack(">I", len(compressed) + 1) + b"\x02" + compressed
        # Pad to 4096-byte sector boundary
        padded_len = ((len(chunk_data) + 4095) // 4096) * 4096
        chunk_data = chunk_data.ljust(padded_len, b"\x00")
        sector_count = padded_len // 4096

        # Write location entry: 3 bytes offset + 1 byte sector count
        offset = slot * 4
        header[offset] = (next_sector >> 16) & 0xFF
        header[offset + 1] = (next_sector >> 8) & 0xFF
        header[offset + 2] = next_sector & 0xFF
        header[offset + 3] = sector_count

        sectors.extend(chunk_data)
        next_sector += sector_count

    path.write_bytes(bytes(header) + bytes(sectors))


def test_analyze_region_basic(tmp_path):
    mca = tmp_path / "r.0.0.mca"
    make_region_with_chunks(mca, [
        {"slot": 0, "inhabited_time": 500, "data_version": 3955},
        {"slot": 1, "inhabited_time": 50, "data_version": 3955},
        {"slot": 2, "inhabited_time": 0, "data_version": 3955},
    ])
    results = analyze_region(mca, threshold=120)
    assert len(results) == 3
    # slot 0: inhabited 500 > 120 => keep
    assert results[(0, 0)]["delete"] is False
    # slot 1: inhabited 50 < 120 => delete
    assert results[(1, 0)]["delete"] is True
    # slot 2: inhabited 0 < 120 => delete
    assert results[(2, 0)]["delete"] is True


def test_analyze_dimension(tmp_path):
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    mca = region_dir / "r.0.0.mca"
    make_region_with_chunks(mca, [
        {"slot": 0, "inhabited_time": 500, "data_version": 3955},
        {"slot": 1, "inhabited_time": 50, "data_version": 3955},
    ])
    stats, grid = analyze_dimension(region_dir, threshold=120)
    assert stats["total"] == 2
    assert stats["delete"] == 1
    assert stats["keep"] == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_regions.py::test_analyze_region_basic -v`
Expected: FAIL — function not found

- [ ] **Step 3: Implement analyze_region and analyze_dimension**

Add to `scripts/migrate_regions.py`:

```python
# Add imports at top
from scripts.migrate_nbt import extract_chunk_tags

TIMESTAMP_OFFSET = 4096  # timestamp table starts after location table
SECTOR_SIZE = 4096


def analyze_region(region_path: Path, threshold: int) -> dict:
    """Analyze all chunks in a region file against an InhabitedTime threshold.

    Returns dict mapping (local_chunk_x, local_chunk_z) to chunk info:
    {"inhabited_time": int, "data_version": int, "delete": bool}
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

        # Read chunk header: 4 bytes length + 1 byte compression
        chunk_len = struct.unpack_from(">I", data, sector_offset)[0]
        compression = data[sector_offset + 4]

        compressed_start = sector_offset + 5
        compressed_end = sector_offset + 4 + chunk_len
        if compressed_end > len(data):
            continue

        compressed_data = data[compressed_start:compressed_end]
        tags = extract_chunk_tags(compressed_data, compression)

        inhabited = tags.get("InhabitedTime") or 0
        dv = tags.get("DataVersion") or 0

        # Chunk coords: region * 32 + local position
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


def analyze_dimension(
    region_dir: Path,
    threshold: int,
) -> tuple[dict, dict]:
    """Analyze all chunks in a dimension's region directory.

    Returns (stats_dict, grid_dict) where:
    - stats_dict: {"total": int, "delete": int, "keep": int}
    - grid_dict: {(cx, cz): {"inhabited_time": int, "data_version": int, "delete": bool}}
    """
    grid = {}
    for mca_file in sorted(region_dir.glob("r.*.*.mca")):
        grid.update(analyze_region(mca_file, threshold))

    total = len(grid)
    delete_count = sum(1 for v in grid.values() if v["delete"])

    stats = {
        "total": total,
        "delete": delete_count,
        "keep": total - delete_count,
    }
    return stats, grid
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_regions.py -v`
Expected: All tests pass (original 4 + new 2)

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_regions.py tests/test_migrate_regions.py
git commit -m "feat: chunk-level analysis with InhabitedTime threshold"
```

---

## Task 3: World Layout Detection

Detect PaperMC (separate folders) vs Vanilla (single folder) world layout, both for local paths and via SSH probe.

**Files:**
- Rewrite: `scripts/migrate_remote.py`
- Rewrite: `tests/test_migrate_remote.py`

- [ ] **Step 1: Write failing tests for layout detection**

```python
# tests/test_migrate_remote.py
from pathlib import Path
from scripts.migrate_remote import detect_local_layout, DimensionPaths


def test_detect_vanilla_layout(tmp_path):
    """Vanilla: everything under one world folder."""
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    (world / "DIM-1" / "region").mkdir(parents=True)
    (world / "DIM1" / "region").mkdir(parents=True)

    paths = detect_local_layout(world)
    assert paths.overworld == world / "region"
    assert paths.nether == world / "DIM-1" / "region"
    assert paths.end == world / "DIM1" / "region"


def test_detect_papermc_layout(tmp_path):
    """PaperMC: separate world folders."""
    root = tmp_path / "serverfiles"
    (root / "world_new" / "region").mkdir(parents=True)
    (root / "world_new_nether" / "DIM-1" / "region").mkdir(parents=True)
    (root / "world_new_the_end" / "DIM1" / "region").mkdir(parents=True)

    paths = detect_local_layout(root / "world_new")
    assert paths.overworld == root / "world_new" / "region"
    assert paths.nether == root / "world_new_nether" / "DIM-1" / "region"
    assert paths.end == root / "world_new_the_end" / "DIM1" / "region"


def test_detect_overworld_only(tmp_path):
    """World with no nether or end."""
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)

    paths = detect_local_layout(world)
    assert paths.overworld == world / "region"
    assert paths.nether is None
    assert paths.end is None


def test_dimension_paths_available(tmp_path):
    """available_dimensions returns only present dimensions."""
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    (world / "DIM-1" / "region").mkdir(parents=True)

    paths = detect_local_layout(world)
    assert set(paths.available_dimensions()) == {"overworld", "nether"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_remote.py -v`
Expected: FAIL — imports fail

- [ ] **Step 3: Implement layout detection**

```python
# scripts/migrate_remote.py
"""World resolution — local layout detection and SSH download."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DimensionPaths:
    """Resolved paths to each dimension's region directory."""
    overworld: Path | None = None
    nether: Path | None = None
    end: Path | None = None

    def available_dimensions(self, check_filesystem: bool = True) -> list[str]:
        """Return list of dimensions that have paths set.

        If check_filesystem=True (default), also verifies dirs exist locally.
        Set check_filesystem=False for remote layouts where paths are relative.
        """
        dims = []
        for name, path in [("overworld", self.overworld), ("nether", self.nether), ("end", self.end)]:
            if path is None:
                continue
            if check_filesystem and not path.is_dir():
                continue
            dims.append(name)
        return dims

    def region_dir(self, dimension: str) -> Path | None:
        return {"overworld": self.overworld, "nether": self.nether, "end": self.end}[dimension]


# Compat: migrate_mca.py imports this for MCA Selector --region flag building
DIMENSION_SUBPATHS = {
    "overworld": "region",
    "nether": "DIM-1/region",
    "end": "DIM1/region",
}

def dimension_region_subpath(dimension: str) -> str:
    """Return relative path from world root to region dir (Vanilla layout)."""
    return DIMENSION_SUBPATHS[dimension]


def detect_local_layout(world_path: Path) -> DimensionPaths:
    """Detect whether a local world uses Vanilla or PaperMC dimension layout.

    Vanilla: world/region/, world/DIM-1/region/, world/DIM1/region/
    PaperMC: world/region/, world_nether/DIM-1/region/, world_the_end/DIM1/region/
    """
    paths = DimensionPaths()

    # Overworld is always under the given path
    ow_region = world_path / "region"
    if ow_region.is_dir():
        paths.overworld = ow_region

    # Try Vanilla layout first
    vanilla_nether = world_path / "DIM-1" / "region"
    vanilla_end = world_path / "DIM1" / "region"

    if vanilla_nether.is_dir():
        paths.nether = vanilla_nether
    if vanilla_end.is_dir():
        paths.end = vanilla_end

    # If Vanilla nether/end not found, try PaperMC layout (sibling dirs)
    if paths.nether is None:
        parent = world_path.parent
        world_name = world_path.name
        paper_nether = parent / f"{world_name}_nether" / "DIM-1" / "region"
        if paper_nether.is_dir():
            paths.nether = paper_nether

    if paths.end is None:
        parent = world_path.parent
        world_name = world_path.name
        paper_end = parent / f"{world_name}_the_end" / "DIM1" / "region"
        if paper_end.is_dir():
            paths.end = paper_end

    return paths


def detect_remote_layout(host: str, remote_path: str) -> DimensionPaths:
    """Detect dimension layout on a remote host via SSH probes."""
    def remote_dir_exists(path: str) -> bool:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", host, f"test -d '{path}' && echo yes"],
            capture_output=True, text=True,
        )
        return "yes" in result.stdout

    paths = DimensionPaths()

    if remote_dir_exists(f"{remote_path}/region"):
        paths.overworld = Path("region")

    # Vanilla
    if remote_dir_exists(f"{remote_path}/DIM-1/region"):
        paths.nether = Path("DIM-1/region")
    # PaperMC
    elif remote_dir_exists(f"{remote_path}_nether/DIM-1/region"):
        paths.nether = Path(f"{Path(remote_path).name}_nether/DIM-1/region")

    if remote_dir_exists(f"{remote_path}/DIM1/region"):
        paths.end = Path("DIM1/region")
    elif remote_dir_exists(f"{remote_path}_the_end/DIM1/region"):
        paths.end = Path(f"{Path(remote_path).name}_the_end/DIM1/region")

    return paths


def download_world(
    host: str,
    remote_path: str,
    local_path: Path,
    dimensions: list[str],
    layout: DimensionPaths,
) -> None:
    """Download world files from remote host via SCP with progress."""
    local_path.mkdir(parents=True, exist_ok=True)

    # Download level.dat
    _scp(host, f"{remote_path}/level.dat", local_path / "level.dat")

    for dim in dimensions:
        region_subpath = layout.region_dir(dim)
        if region_subpath is None:
            print(f"  Skipping {dim} (not found on remote)", file=sys.stderr)
            continue

        # For PaperMC layout, remote path may be relative to parent
        if str(region_subpath).startswith(Path(remote_path).name + "_"):
            remote_region = f"{Path(remote_path).parent}/{region_subpath}"
        else:
            remote_region = f"{remote_path}/{region_subpath}"

        local_region = local_path / region_subpath
        local_region.mkdir(parents=True, exist_ok=True)

        print(f"  Downloading {dim}...", file=sys.stderr)
        _scp_recursive(host, remote_region, local_region)


def _scp(host: str, remote: str, local: Path) -> None:
    """SCP a single file."""
    local.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["scp", f"{host}:{remote}", str(local)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: SCP failed: {result.stderr}", file=sys.stderr)
        sys.exit(2)  # exit code 2 = dependency/environment error


def _scp_recursive(host: str, remote_dir: str, local_dir: Path) -> None:
    """SCP a directory's contents recursively."""
    result = subprocess.run(
        ["scp", "-r", f"{host}:{remote_dir}/*", str(local_dir)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: SCP failed: {result.stderr}", file=sys.stderr)
        sys.exit(2)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_remote.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_remote.py tests/test_migrate_remote.py
git commit -m "feat: PaperMC and Vanilla world layout detection"
```

---

## Task 4: HTML Preview Generator

Generate a self-contained HTML file with a canvas grid showing keep/delete/unexplored chunks per dimension.

**Files:**
- Create: `scripts/migrate_html.py`
- Create: `tests/test_migrate_html.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_migrate_html.py
from pathlib import Path
from scripts.migrate_html import generate_html


def test_generate_html_contains_structure():
    """HTML output should be self-contained with expected elements."""
    dimensions = {
        "overworld": {
            "stats": {"total": 100, "delete": 60, "keep": 40},
            "grid": {
                (0, 0): {"delete": False, "inhabited_time": 500},
                (1, 0): {"delete": True, "inhabited_time": 50},
                (0, 1): {"delete": True, "inhabited_time": 0},
            },
        }
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "<!DOCTYPE html>" in html
    assert "InhabitedTime" in html
    assert "canvas" in html.lower()
    assert "Overworld" in html
    # Data should be embedded as base64
    assert "base64" in html.lower() or "data:" in html


def test_generate_html_multiple_dimensions():
    """Multi-dimension output should have tabs."""
    dimensions = {
        "overworld": {
            "stats": {"total": 100, "delete": 60, "keep": 40},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 500}},
        },
        "nether": {
            "stats": {"total": 50, "delete": 30, "keep": 20},
            "grid": {(0, 0): {"delete": True, "inhabited_time": 10}},
        },
    }
    html = generate_html(dimensions, query="InhabitedTime < 120")
    assert "Overworld" in html
    assert "Nether" in html


def test_generate_html_writes_file(tmp_path):
    """generate_html_file should write to disk."""
    from scripts.migrate_html import generate_html_file
    dimensions = {
        "overworld": {
            "stats": {"total": 10, "delete": 5, "keep": 5},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 200}},
        },
    }
    out = tmp_path / "preview.html"
    generate_html_file(dimensions, query="InhabitedTime < 120", output_path=out)
    assert out.exists()
    content = out.read_text()
    assert "<!DOCTYPE html>" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_html.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement migrate_html.py**

```python
# scripts/migrate_html.py
"""Generate self-contained HTML preview of migration chunk analysis."""

import base64
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

from scripts.migrate_nbt import inhabited_bucket

DIMENSION_LABELS = {"overworld": "Overworld", "nether": "Nether", "end": "End"}


def _pack_grid_binary(grid: dict) -> tuple[bytes, dict]:
    """Pack chunk grid into a binary buffer with metadata.

    Returns (binary_data, metadata_dict).
    Binary: Uint8 per chunk in row-major order.
    Bit 7: exists, Bit 6: delete, Bits 0-5: inhabited bucket.
    """
    if not grid:
        return b"", {"min_cx": 0, "max_cx": 0, "min_cz": 0, "max_cz": 0, "cols": 1, "rows": 1}

    coords = list(grid.keys())
    min_cx = min(c[0] for c in coords)
    max_cx = max(c[0] for c in coords)
    min_cz = min(c[1] for c in coords)
    max_cz = max(c[1] for c in coords)
    cols = max_cx - min_cx + 1
    rows = max_cz - min_cz + 1

    buf = bytearray(cols * rows)
    for (cx, cz), info in grid.items():
        px = cx - min_cx
        pz = cz - min_cz
        inhabited = info.get("inhabited_time", 0)
        bucket = inhabited_bucket(inhabited)
        byte_val = 0x80  # exists bit
        if info["delete"]:
            byte_val |= 0x40  # delete bit
        byte_val |= (bucket & 0x3F)
        buf[pz * cols + px] = byte_val

    meta = {
        "min_cx": min_cx, "max_cx": max_cx,
        "min_cz": min_cz, "max_cz": max_cz,
        "cols": cols, "rows": rows,
    }
    return bytes(buf), meta


def generate_html(dimensions: dict, query: str) -> str:
    """Generate self-contained HTML string for migration preview.

    dimensions: {"overworld": {"stats": {...}, "grid": {(cx,cz): {...}}}, ...}
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Pack each dimension's grid
    dim_data = {}
    for dim_key, dim_info in dimensions.items():
        binary, meta = _pack_grid_binary(dim_info["grid"])
        meta["total"] = dim_info["stats"]["total"]
        meta["delete"] = dim_info["stats"]["delete"]
        meta["keep"] = dim_info["stats"]["keep"]
        dim_data[dim_key] = {
            "binary_b64": base64.b64encode(binary).decode("ascii"),
            "meta": meta,
            "label": DIMENSION_LABELS.get(dim_key, dim_key),
        }

    dim_json = json.dumps(dim_data)
    dim_keys = list(dimensions.keys())
    first_dim = dim_keys[0]

    # Build tab buttons
    tabs_html = " ".join(
        f'<button class="tab{"" if dk != first_dim else " active"}" '
        f'onclick="switchDim(\'{dk}\')">{DIMENSION_LABELS.get(dk, dk)}</button>'
        for dk in dim_keys
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Migration Preview</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #1a1a2e; color: #e0e0e0; font-family: monospace; }}
  .header {{ padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }}
  .header h1 {{ color: #6dd; font-size: 16px; font-weight: bold; }}
  .header .meta {{ color: #888; font-size: 12px; }}
  .tabs {{ display: flex; gap: 8px; padding: 0 20px 12px; }}
  .tab {{ background: #16213e; color: #888; border: 1px solid #333; padding: 6px 16px;
          border-radius: 4px; font-size: 13px; font-family: monospace; cursor: pointer; }}
  .tab.active {{ background: #6dd; color: #1a1a2e; border-color: #6dd; font-weight: bold; }}
  .canvas-wrap {{ display: flex; justify-content: center; padding: 8px 20px; }}
  canvas {{ image-rendering: pixelated; border: 1px solid #333; max-width: 100%; }}
  .legend {{ display: flex; gap: 20px; justify-content: center; padding: 12px 0; font-size: 13px; }}
  .legend span {{ display: flex; align-items: center; gap: 4px; }}
  .swatch {{ width: 12px; height: 12px; border-radius: 2px; display: inline-block; }}
  .stats {{ background: #16213e; border-radius: 6px; padding: 12px 16px; margin: 12px 20px; }}
  .stats-row {{ display: flex; justify-content: space-between; font-size: 12px; color: #aaa; }}
  .bar {{ background: #2d8a4e; height: 6px; border-radius: 3px; margin-top: 8px; position: relative; }}
  .bar-fill {{ background: #c0392b; height: 100%; border-radius: 3px 0 0 3px; position: absolute; left: 0; }}
</style>
</head>
<body>
<div class="header">
  <h1>Migration Preview</h1>
  <span class="meta">{query} | {timestamp}</span>
</div>
<div class="tabs">{tabs_html}</div>
<div class="canvas-wrap"><canvas id="grid" width="800" height="800"></canvas></div>
<div class="legend">
  <span><span class="swatch" style="background:#2d8a4e"></span> Keep</span>
  <span><span class="swatch" style="background:#c0392b"></span> Delete</span>
  <span><span class="swatch" style="background:#1a1a2e;border:1px solid #333"></span> Unexplored</span>
</div>
<div class="stats">
  <div class="stats-row">
    <span id="stat-total"></span>
    <span id="stat-pct"></span>
    <span id="stat-query">Query: {query}</span>
  </div>
  <div class="bar"><div class="bar-fill" id="bar-fill"></div></div>
</div>
<script>
const DIMS = {dim_json};
let currentDim = "{first_dim}";

function switchDim(dk) {{
  currentDim = dk;
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelector(`.tab[onclick*="${{dk}}"]`).classList.add("active");
  render();
}}

function render() {{
  const dim = DIMS[currentDim];
  const m = dim.meta;
  const raw = atob(dim.binary_b64);
  const buf = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) buf[i] = raw.charCodeAt(i);

  const canvas = document.getElementById("grid");
  const scale = Math.max(1, Math.min(
    Math.floor(800 / m.cols),
    Math.floor(800 / m.rows)
  ));
  canvas.width = m.cols * scale;
  canvas.height = m.rows * scale;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let z = 0; z < m.rows; z++) {{
    for (let x = 0; x < m.cols; x++) {{
      const v = buf[z * m.cols + x];
      if (!(v & 0x80)) continue;
      const del = (v & 0x40) !== 0;
      ctx.fillStyle = del ? "#c0392b" : "#2d8a4e";
      ctx.fillRect(x * scale, z * scale, scale, scale);
    }}
  }}

  const pct = m.total > 0 ? (m.delete / m.total * 100).toFixed(1) : "0.0";
  document.getElementById("stat-total").textContent =
    `Total: ${{m.total.toLocaleString()}} | Delete: ${{m.delete.toLocaleString()}} | Keep: ${{m.keep.toLocaleString()}}`;
  document.getElementById("stat-pct").textContent = `${{pct}}% trimmed`;
  document.getElementById("bar-fill").style.width = `${{pct}}%`;
}}

render();
</script>
</body>
</html>'''


def generate_html_file(dimensions: dict, query: str, output_path: Path) -> None:
    """Generate and write HTML preview to a file."""
    html = generate_html(dimensions, query)
    output_path.write_text(html, encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_html.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_html.py tests/test_migrate_html.py
git commit -m "feat: standalone HTML migration preview generator"
```

---

## Task 5: Raw Binary Output

Generate the overlay binary file for the chunk inspector.

**Files:**
- Create: `scripts/migrate_raw.py`
- Create: `tests/test_migrate_raw.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_migrate_raw.py
import json
from pathlib import Path
from scripts.migrate_raw import generate_raw_file


def test_generate_raw_single_dimension(tmp_path):
    """Single dimension uses exact filename."""
    dimensions = {
        "overworld": {
            "stats": {"total": 3, "delete": 2, "keep": 1},
            "grid": {
                (0, 0): {"delete": False, "inhabited_time": 500, "data_version": 3955},
                (1, 0): {"delete": True, "inhabited_time": 50, "data_version": 3955},
                (0, 1): {"delete": True, "inhabited_time": 0, "data_version": 3955},
            },
        },
    }
    out = tmp_path / "migration.bin"
    generate_raw_file(dimensions, query="InhabitedTime < 120", output_path=out)

    assert out.exists()
    data = out.read_bytes()
    # 2x2 grid (min 0,0 max 1,1) = 4 bytes
    assert len(data) == 4

    # JSON metadata
    meta_path = tmp_path / "migration.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert meta["total"] == 3
    assert meta["delete"] == 2
    assert meta["cols"] == 2
    assert meta["rows"] == 2


def test_generate_raw_multi_dimension(tmp_path):
    """Multiple dimensions append dimension suffix."""
    dimensions = {
        "overworld": {
            "stats": {"total": 1, "delete": 0, "keep": 1},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 500}},
        },
        "nether": {
            "stats": {"total": 1, "delete": 1, "keep": 0},
            "grid": {(0, 0): {"delete": True, "inhabited_time": 10}},
        },
    }
    out = tmp_path / "migration.bin"
    generate_raw_file(dimensions, query="InhabitedTime < 120", output_path=out)

    assert (tmp_path / "migration-overworld.bin").exists()
    assert (tmp_path / "migration-nether.bin").exists()
    assert (tmp_path / "migration-overworld.json").exists()
    assert (tmp_path / "migration-nether.json").exists()
    # Original filename should NOT exist
    assert not out.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_raw.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement migrate_raw.py**

```python
# scripts/migrate_raw.py
"""Generate binary overlay data for the chunk inspector."""

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.migrate_nbt import inhabited_bucket


def _pack_dimension(grid: dict) -> tuple[bytes, dict]:
    """Pack a dimension's grid into Uint8 binary + metadata.

    Bit 7: exists, Bit 6: delete, Bits 0-5: inhabited bucket.
    """
    if not grid:
        return b"", {"min_cx": 0, "max_cx": 0, "min_cz": 0, "max_cz": 0, "cols": 1, "rows": 1}

    coords = list(grid.keys())
    min_cx = min(c[0] for c in coords)
    max_cx = max(c[0] for c in coords)
    min_cz = min(c[1] for c in coords)
    max_cz = max(c[1] for c in coords)
    cols = max_cx - min_cx + 1
    rows = max_cz - min_cz + 1

    buf = bytearray(cols * rows)
    for (cx, cz), info in grid.items():
        px = cx - min_cx
        pz = cz - min_cz
        bucket = inhabited_bucket(info.get("inhabited_time", 0))
        byte_val = 0x80  # exists
        if info["delete"]:
            byte_val |= 0x40
        byte_val |= (bucket & 0x3F)
        buf[pz * cols + px] = byte_val

    meta = {
        "min_cx": min_cx, "max_cx": max_cx,
        "min_cz": min_cz, "max_cz": max_cz,
        "cols": cols, "rows": rows,
    }
    return bytes(buf), meta


def generate_raw_file(dimensions: dict, query: str, output_path: Path) -> None:
    """Generate binary overlay file(s) for the chunk inspector.

    Single dimension: writes exact output_path + .json metadata.
    Multiple dimensions: writes output_path stem + dimension suffix for each.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    stem = output_path.stem
    parent = output_path.parent
    suffix = output_path.suffix

    if len(dimensions) == 1:
        dim_key = list(dimensions.keys())[0]
        dim_info = dimensions[dim_key]
        binary, meta = _pack_dimension(dim_info["grid"])
        meta.update(dim_info["stats"])
        meta["query"] = query
        meta["timestamp"] = timestamp
        meta["dimension"] = dim_key

        output_path.write_bytes(binary)
        meta_path = parent / f"{stem}.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    else:
        for dim_key, dim_info in dimensions.items():
            binary, meta = _pack_dimension(dim_info["grid"])
            meta.update(dim_info["stats"])
            meta["query"] = query
            meta["timestamp"] = timestamp
            meta["dimension"] = dim_key

            bin_path = parent / f"{stem}-{dim_key}{suffix}"
            bin_path.write_bytes(binary)
            meta_path = parent / f"{stem}-{dim_key}.json"
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_raw.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate_raw.py tests/test_migrate_raw.py
git commit -m "feat: binary overlay output for chunk inspector"
```

---

## Task 6: CLI Argument Parsing (Rewrite)

Replace the old arg parsing with the new spec: positional world-path, `--html`, `--raw`, `--dangerously-perform-the-trim`, etc.

**Files:**
- Rewrite: `scripts/migrate.py` (arg parsing only)
- Rewrite: `tests/test_migrate_args.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_migrate_args.py
import pytest
from scripts.migrate import parse_args


def test_local_world_with_threshold():
    args = parse_args(["./world", "--threshold", "120", "--html", "out.html"])
    assert args.world_path == "./world"
    assert args.threshold == 120
    assert args.query is None
    assert args.html == "out.html"


def test_ssh_download():
    args = parse_args([
        "--host", "minecraft",
        "--remote-path", "/home/minecraft/serverfiles",
        "--html", "out.html",
    ])
    assert args.host == "minecraft"
    assert args.remote_path == "/home/minecraft/serverfiles"
    assert args.world_path is None


def test_default_threshold():
    args = parse_args(["./world", "--html", "out.html"])
    assert args.threshold == 120
    assert args.query is None


def test_query_mode():
    args = parse_args([
        "./world",
        "--query", "InhabitedTime < 600 AND DataVersion < 2860",
        "--mcaselector", "./mca.jar",
        "--html", "out.html",
    ])
    assert args.query == "InhabitedTime < 600 AND DataVersion < 2860"
    assert args.threshold is None


def test_threshold_and_query_exclusive():
    with pytest.raises(SystemExit):
        parse_args([
            "./world", "--threshold", "120",
            "--query", "foo", "--mcaselector", "./mca.jar",
        ])


def test_query_requires_mcaselector():
    with pytest.raises(SystemExit):
        parse_args(["./world", "--query", "foo", "--html", "out.html"])


def test_both_world_and_host_error():
    with pytest.raises(SystemExit):
        parse_args([
            "./world", "--host", "mc", "--remote-path", "/world",
            "--html", "out.html",
        ])


def test_dimensions_default_not_set():
    args = parse_args(["./world", "--html", "out.html"])
    assert args.dimensions is None  # auto-detect


def test_dimensions_explicit():
    args = parse_args([
        "./world", "--dimensions", "overworld", "nether",
        "--html", "out.html",
    ])
    assert args.dimensions == ["overworld", "nether"]


def test_dangerously_trim_flag():
    args = parse_args(["./world", "--dangerously-perform-the-trim"])
    assert args.dangerously_perform_the_trim is True


def test_safety_pct_default():
    args = parse_args(["./world", "--html", "out.html"])
    assert args.safety_pct == 90


def test_raw_output():
    args = parse_args(["./world", "--raw", "migration.bin"])
    assert args.raw == "migration.bin"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_args.py -v`
Expected: FAIL — old parse_args incompatible

- [ ] **Step 3: Implement new parse_args**

Rewrite `scripts/migrate.py`:

```python
#!/usr/bin/env python3
"""Migration preview CLI — analyze, visualize, and optionally trim Minecraft world chunks."""

import argparse
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Minecraft world chunks, generate migration preview reports, "
                    "and optionally trim low-activity chunks.",
    )

    # World source (positional or SSH)
    parser.add_argument(
        "world_path", nargs="?", default=None,
        help="Local world directory path",
    )
    parser.add_argument("--host", help="SSH host to download from")
    parser.add_argument("--remote-path", help="Remote world directory path")

    # Dimensions
    parser.add_argument(
        "--dimensions", nargs="+", default=None,
        choices=["overworld", "nether", "end"],
        help="Dimensions to analyze (default: auto-detect all present)",
    )

    # Query
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument(
        "--threshold", type=int,
        help="InhabitedTime threshold in ticks (default: 120 = 6 seconds)",
    )
    query_group.add_argument(
        "--query",
        help="Full MCA Selector query string (requires --mcaselector)",
    )
    parser.add_argument("--mcaselector", help="Path to MCA Selector JAR")

    # Outputs
    parser.add_argument("--html", help="Generate standalone HTML preview at this path")
    parser.add_argument("--raw", help="Generate binary overlay data at this path")
    parser.add_argument(
        "--dangerously-perform-the-trim", action="store_true",
        help="Actually delete matching chunks (destructive!)",
    )

    # Safety
    parser.add_argument(
        "--safety-pct", type=int, default=90,
        help="Abort trim if deletion exceeds this %% per dimension (default: 90)",
    )
    parser.add_argument("--force", action="store_true", help="Override safety abort")

    args = parser.parse_args(argv)

    # Validation: world source
    if args.world_path and args.host:
        parser.error("Cannot specify both a local world path and --host")
    if not args.world_path and not args.host:
        parser.error("Provide a local world path or --host + --remote-path")
    if args.host and not args.remote_path:
        parser.error("--host requires --remote-path")

    # Validation: query
    if args.query and not args.mcaselector:
        parser.error("--query requires --mcaselector")

    # Default threshold
    if args.threshold is None and args.query is None:
        args.threshold = 120

    return args
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_args.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate.py tests/test_migrate_args.py
git commit -m "feat: new CLI arg parsing for migration preview"
```

---

## Task 7: Pipeline Orchestration

Wire everything together: resolve world, analyze dimensions, generate outputs, optionally trim.

**Files:**
- Modify: `scripts/migrate.py` — add pipeline functions and `main()`
- Create: `tests/test_migrate_e2e.py`

- [ ] **Step 1: Write failing e2e test**

```python
# tests/test_migrate_e2e.py
"""End-to-end pipeline tests with real region files."""
import json
from pathlib import Path
from tests.test_migrate_regions import make_region_with_chunks


def setup_world(tmp_path, chunks_per_region=None):
    """Create a minimal Vanilla-layout world."""
    if chunks_per_region is None:
        chunks_per_region = [
            {"slot": 0, "inhabited_time": 500, "data_version": 3955},
            {"slot": 1, "inhabited_time": 50, "data_version": 3955},
            {"slot": 2, "inhabited_time": 0, "data_version": 3955},
        ]
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    make_region_with_chunks(world / "region" / "r.0.0.mca", chunks_per_region)
    (world / "level.dat").write_bytes(b"\x00" * 16)
    return world


def test_full_pipeline_html(tmp_path):
    """Pipeline should produce HTML output."""
    world = setup_world(tmp_path)
    html_out = tmp_path / "preview.html"

    from scripts.migrate import run_pipeline, parse_args
    args = parse_args([str(world), "--threshold", "120", "--html", str(html_out)])
    code = run_pipeline(args)

    assert code == 0
    assert html_out.exists()
    content = html_out.read_text()
    assert "Migration Preview" in content
    assert "Overworld" in content


def test_full_pipeline_raw(tmp_path):
    """Pipeline should produce raw binary output."""
    world = setup_world(tmp_path)
    raw_out = tmp_path / "migration.bin"

    from scripts.migrate import run_pipeline, parse_args
    args = parse_args([str(world), "--threshold", "120", "--raw", str(raw_out)])
    code = run_pipeline(args)

    assert code == 0
    assert raw_out.exists()
    meta_path = tmp_path / "migration.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert meta["total"] == 3
    assert meta["delete"] == 2  # slots 1 and 2 have inhabited < 120


def test_full_pipeline_stats_only(tmp_path, capsys):
    """No output flags = just print stats."""
    world = setup_world(tmp_path)

    from scripts.migrate import run_pipeline, parse_args
    args = parse_args([str(world), "--threshold", "120"])
    code = run_pipeline(args)

    assert code == 0
    captured = capsys.readouterr()
    assert "Overworld" in captured.err
    assert "3" in captured.err  # total chunks


def test_trim_actually_deletes_chunks(tmp_path):
    """--dangerously-perform-the-trim should zero matching chunks in region files."""
    import struct
    # 3 chunks: slot 0 (keep, high inhabited), slots 1-2 (delete, low inhabited)
    world = setup_world(tmp_path, [
        {"slot": 0, "inhabited_time": 500, "data_version": 3955},
        {"slot": 1, "inhabited_time": 50, "data_version": 3955},
        {"slot": 2, "inhabited_time": 0, "data_version": 3955},
    ])

    from scripts.migrate import run_pipeline, parse_args
    args = parse_args([str(world), "--threshold", "120", "--dangerously-perform-the-trim"])
    code = run_pipeline(args)
    assert code == 0

    # Verify: slot 0 should still have data, slots 1-2 should be zeroed
    mca = world / "region" / "r.0.0.mca"
    data = mca.read_bytes()
    # Slot 0: should be non-zero
    assert struct.unpack_from(">I", data, 0)[0] != 0
    # Slot 1: should be zeroed
    assert struct.unpack_from(">I", data, 4)[0] == 0
    # Slot 2: should be zeroed
    assert struct.unpack_from(">I", data, 8)[0] == 0


def test_safety_abort_blocks_trim(tmp_path):
    """Safety check should block trim but still generate outputs."""
    # All chunks have inhabited_time=0 -> 100% deletion
    world = setup_world(tmp_path, [
        {"slot": i, "inhabited_time": 0, "data_version": 3955}
        for i in range(10)
    ])
    html_out = tmp_path / "preview.html"

    from scripts.migrate import run_pipeline, parse_args
    args = parse_args([
        str(world), "--threshold", "120",
        "--html", str(html_out),
        "--dangerously-perform-the-trim",
    ])
    code = run_pipeline(args)

    assert code == 1  # safety abort
    assert html_out.exists()  # HTML still generated
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/test_migrate_e2e.py -v`
Expected: FAIL — `run_pipeline` not found

- [ ] **Step 3: Implement the pipeline**

Add to `scripts/migrate.py` after `parse_args`:

```python
from scripts.migrate_regions import analyze_dimension
from scripts.migrate_remote import detect_local_layout, detect_remote_layout, download_world
from scripts.migrate_display import format_stats_table, format_safety_abort, format_report
from scripts.migrate_html import generate_html_file
from scripts.migrate_raw import generate_raw_file
from scripts.migrate_mca import build_select_command, build_delete_command, run_mcaselector, count_selected_chunks
from scripts.migrate_regions import count_chunks_in_directory

DIMENSION_LABELS = {"overworld": "Overworld", "nether": "Nether", "end": "End"}


def run_pipeline(args: argparse.Namespace) -> int:
    """Execute the migration preview pipeline. Returns exit code."""

    # Step 1: Resolve world
    if args.host:
        layout = detect_remote_layout(args.host, args.remote_path)
        world_name = Path(args.remote_path).name
        local_path = Path("./migration-work") / world_name
        dims = args.dimensions or layout.available_dimensions(check_filesystem=False)
        download_world(args.host, args.remote_path, local_path, dims, layout)
        world_path = local_path
        # Re-detect locally after download
        layout = detect_local_layout(world_path)
    else:
        world_path = Path(args.world_path)
        layout = detect_local_layout(world_path)

    dims = args.dimensions or layout.available_dimensions()
    if not dims:
        print("ERROR: No dimensions found in world.", file=sys.stderr)
        return 2

    # Step 2: Analyze
    print("Analyzing chunks...", file=sys.stderr)
    dimensions = {}
    for dim in dims:
        region_dir = layout.region_dir(dim)
        if region_dir is None or not region_dir.is_dir():
            print(f"  Skipping {dim} (not found)", file=sys.stderr)
            continue

        if args.threshold is not None:
            # Pure Python analysis
            stats, grid = analyze_dimension(region_dir, args.threshold)
        else:
            # MCA Selector mode
            total = count_chunks_in_directory(region_dir)
            csv_path = Path(f"./migration-work/selection-{dim}.csv")
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            select_cmd = build_select_command(
                mcaselector_jar=Path(args.mcaselector),
                world_dir=world_path,
                dimension=dim,
                query=args.query,
                output_csv=csv_path,
            )
            run_mcaselector(select_cmd, f"Selecting {DIMENSION_LABELS[dim]} chunks")
            delete_count = count_selected_chunks(csv_path)
            stats = {"total": total, "delete": delete_count, "keep": total - delete_count}
            grid = {}  # MCA Selector mode has no per-chunk data for visualization

        dimensions[dim] = {
            "stats": {**stats, "dimension": DIMENSION_LABELS.get(dim, dim)},
            "grid": grid,
        }

    # Step 3: Print stats
    stats_list = [d["stats"] for d in dimensions.values()]
    table = format_stats_table(stats_list)
    print(f"\n{table}\n", file=sys.stderr)

    # Step 4: Generate outputs (always, even if safety check will fire)
    query_str = args.query or f"InhabitedTime < {args.threshold}"

    if args.html:
        generate_html_file(dimensions, query=query_str, output_path=Path(args.html))
        print(f"HTML preview: {args.html}", file=sys.stderr)

    if args.raw:
        generate_raw_file(dimensions, query=query_str, output_path=Path(args.raw))
        print(f"Raw output: {args.raw}", file=sys.stderr)

    # Step 5: Safety check + trim
    if args.dangerously_perform_the_trim:
        # Safety check
        if not args.force:
            for dim, dim_data in dimensions.items():
                s = dim_data["stats"]
                if s["total"] == 0:
                    continue
                pct = s["delete"] / s["total"] * 100
                if pct > args.safety_pct:
                    msg = format_safety_abort(s["dimension"], pct)
                    print(msg, file=sys.stderr)
                    return 1

        # Trim
        print("Trimming chunks...", file=sys.stderr)
        if args.threshold is not None:
            _trim_pure_python(dimensions, layout, dims)
        else:
            _trim_mcaselector(args, world_path, dims)

        report = format_report(stats_list, str(world_path), dims)
        print(f"\n{report}", file=sys.stderr)

    return 0


def _trim_pure_python(dimensions: dict, layout, dims: list[str]) -> None:
    """Trim chunks by zeroing location/timestamp entries in region files."""
    import struct

    for dim in dims:
        region_dir = layout.region_dir(dim)
        if region_dir is None:
            continue
        grid = dimensions[dim]["grid"]
        chunks_to_delete = {k for k, v in grid.items() if v["delete"]}

        for mca_file in sorted(region_dir.glob("r.*.*.mca")):
            parts = mca_file.stem.split(".")
            region_x, region_z = int(parts[1]), int(parts[2])

            data = bytearray(mca_file.read_bytes())
            modified = False

            for cx, cz in list(chunks_to_delete):
                # Check if this chunk belongs to this region
                if cx // 32 != region_x or cz // 32 != region_z:
                    continue
                local_x = cx % 32
                local_z = cz % 32
                slot = local_z * 32 + local_x
                loc_offset = slot * 4
                ts_offset = 4096 + slot * 4

                # Zero location and timestamp
                data[loc_offset:loc_offset + 4] = b"\x00\x00\x00\x00"
                data[ts_offset:ts_offset + 4] = b"\x00\x00\x00\x00"
                modified = True

            if modified:
                # Check if all entries are zero -> delete file
                all_zero = all(
                    struct.unpack_from(">I", data, i * 4)[0] == 0
                    for i in range(1024)
                )
                if all_zero:
                    mca_file.unlink()
                else:
                    mca_file.write_bytes(bytes(data))


def _trim_mcaselector(args, world_path: Path, dims: list[str]) -> None:
    """Trim chunks via MCA Selector --mode delete."""
    for dim in dims:
        delete_cmd = build_delete_command(
            mcaselector_jar=Path(args.mcaselector),
            world_dir=world_path,
            dimension=dim,
            query=args.query,
        )
        run_mcaselector(delete_cmd, f"Trimming {DIMENSION_LABELS[dim]}")


def main() -> None:
    args = parse_args()
    code = run_pipeline(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests**

Run: `cd C:/Users/leole/Documents/code/minecraft && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add scripts/migrate.py tests/test_migrate_e2e.py
git commit -m "feat: pipeline orchestration with HTML, raw, and trim outputs"
```

---

## Task 8: Smoke Test

**Files:** None (verification only)

- [ ] **Step 1: Verify --help**

Run: `cd C:/Users/leole/Documents/code/minecraft && python scripts/migrate.py --help`
Expected: Help text with all arguments.

- [ ] **Step 2: Test against a real world copy (if available)**

```bash
# Download world and generate HTML preview
python scripts/migrate.py \
  --host minecraft \
  --remote-path /home/minecraft/serverfiles/world_new \
  --threshold 120 \
  --dimensions overworld \
  --html preview.html
```

Open `preview.html` in a browser — verify green/red grid appears.

- [ ] **Step 3: Commit any fixes**

```bash
git add -A && git commit -m "fix: smoke test adjustments"
```

---

## Task Summary

| Task | What | Tests | Deps |
|------|------|-------|------|
| 1 | NBT tag reader | 3 | — |
| 2 | Chunk analysis (extend regions) | 2+ | Task 1 |
| 3 | World layout detection (rewrite remote) | 4 | — |
| 4 | HTML preview generator | 3 | — |
| 5 | Raw binary output | 2 | — |
| 6 | CLI arg parsing (rewrite) | 12 | — |
| 7 | Pipeline orchestration | 5 | Tasks 1-6 |
| 8 | Smoke test | — | Task 7 |

Tasks 1, 3, 4, 5, 6 are independent. Task 2 depends on Task 1. Task 7 depends on all others. Task 8 depends on Task 7.
