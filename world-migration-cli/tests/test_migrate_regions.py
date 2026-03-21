# tests/test_migrate_regions.py
from pathlib import Path
from migrate_regions import count_chunks_in_region, count_chunks_in_directory

FIXTURES = Path(__file__).parent / "fixtures"


def test_count_chunks_populated_region():
    assert count_chunks_in_region(FIXTURES / "r.0.0.mca") == 5


def test_count_chunks_empty_region():
    assert count_chunks_in_region(FIXTURES / "r.0.1.mca") == 0


def test_count_chunks_in_directory(tmp_path):
    import shutil
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    shutil.copy(FIXTURES / "r.0.0.mca", region_dir / "r.0.0.mca")
    shutil.copy(FIXTURES / "r.0.1.mca", region_dir / "r.-1.0.mca")
    assert count_chunks_in_directory(region_dir) == 5


def test_count_chunks_nonexistent_dir(tmp_path):
    assert count_chunks_in_directory(tmp_path / "nope") == 0


# ---------------------------------------------------------------------------
# analyze_region / analyze_dimension tests
# ---------------------------------------------------------------------------

from migrate_regions import analyze_region, analyze_dimension


def make_region_with_chunks(path, chunks):
    """Build a .mca file with real chunk data.
    chunks: list of {"slot": int, "inhabited_time": int, "data_version": int}
    """
    import struct
    import zlib

    header = bytearray(8192)
    sectors = bytearray()
    next_sector = 2  # sectors 0-1 are the header

    for chunk in chunks:
        slot = chunk["slot"]
        # Build minimal NBT: root compound with DataVersion (int) and InhabitedTime (long)
        nbt = b"\x0a\x00\x00"  # root compound, empty name
        # DataVersion tag
        dv_name = b"DataVersion"
        nbt += b"\x03" + struct.pack(">H", len(dv_name)) + dv_name + struct.pack(">i", chunk["data_version"])
        # InhabitedTime tag
        it_name = b"InhabitedTime"
        nbt += b"\x04" + struct.pack(">H", len(it_name)) + it_name + struct.pack(">q", chunk["inhabited_time"])
        nbt += b"\x00"  # end tag

        compressed = zlib.compress(nbt)
        chunk_data = struct.pack(">I", len(compressed) + 1) + b"\x02" + compressed
        padded_len = ((len(chunk_data) + 4095) // 4096) * 4096
        chunk_data = chunk_data.ljust(padded_len, b"\x00")
        sector_count = padded_len // 4096

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
    assert results[(0, 0)]["delete"] is False  # 500 > 120
    assert results[(1, 0)]["delete"] is True   # 50 < 120
    assert results[(2, 0)]["delete"] is True   # 0 < 120


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
