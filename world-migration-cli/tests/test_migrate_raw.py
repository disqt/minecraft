import json
from pathlib import Path
from migrate_raw import generate_raw_file


def test_generate_raw_single_dimension(tmp_path):
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
    assert len(data) == 4  # 2x2 grid
    # JSON metadata
    meta_path = tmp_path / "migration.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert meta["total"] == 3
    assert meta["delete"] == 2
    assert meta["cols"] == 2
    assert meta["rows"] == 2


def test_generate_raw_multi_dimension(tmp_path):
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
    assert not out.exists()  # Original filename NOT created


# ---------------------------------------------------------------------------
# Additional behavioural tests
# ---------------------------------------------------------------------------

def test_bit_encoding_exists_keep(tmp_path):
    """A kept chunk sets bit 7 (exists=1), bit 6 = 0, bits 0-5 = bucket."""
    from migrate_nbt import inhabited_bucket
    dimensions = {
        "overworld": {
            "stats": {"total": 1, "delete": 0, "keep": 1},
            "grid": {(0, 0): {"delete": False, "inhabited_time": 500}},
        },
    }
    out = tmp_path / "out.bin"
    generate_raw_file(dimensions, query="q", output_path=out)
    byte = out.read_bytes()[0]
    assert byte & 0x80  # bit 7 set (exists)
    assert not (byte & 0x40)  # bit 6 clear (not delete)
    assert (byte & 0x3F) == inhabited_bucket(500)


def test_bit_encoding_exists_delete(tmp_path):
    """A deleted chunk sets both bit 7 (exists) and bit 6 (delete)."""
    dimensions = {
        "overworld": {
            "stats": {"total": 1, "delete": 1, "keep": 0},
            "grid": {(0, 0): {"delete": True, "inhabited_time": 50}},
        },
    }
    out = tmp_path / "out.bin"
    generate_raw_file(dimensions, query="q", output_path=out)
    byte = out.read_bytes()[0]
    assert byte & 0x80  # exists
    assert byte & 0x40  # delete


def test_absent_chunk_is_zero(tmp_path):
    """Grid positions with no chunk entry must be 0x00."""
    # Sparse grid: only (0,0) and (1,1) are populated — (0,1) and (1,0) absent
    dimensions = {
        "overworld": {
            "stats": {"total": 2, "delete": 0, "keep": 2},
            "grid": {
                (0, 0): {"delete": False, "inhabited_time": 100},
                (1, 1): {"delete": False, "inhabited_time": 100},
            },
        },
    }
    out = tmp_path / "out.bin"
    generate_raw_file(dimensions, query="q", output_path=out)
    data = out.read_bytes()
    assert len(data) == 4  # 2x2
    # (0,1) is grid[1*2+0] = index 2; (1,0) is grid[0*2+1] = index 1
    assert data[1] == 0x00  # (1,0) absent
    assert data[2] == 0x00  # (0,1) absent


def test_metadata_fields(tmp_path):
    """JSON metadata contains all required keys with correct values."""
    dimensions = {
        "overworld": {
            "stats": {"total": 2, "delete": 1, "keep": 1},
            "grid": {
                (10, -5): {"delete": False, "inhabited_time": 800},
                (12, -3): {"delete": True, "inhabited_time": 30},
            },
        },
    }
    out = tmp_path / "result.bin"
    generate_raw_file(dimensions, query="InhabitedTime < 120", output_path=out)
    meta = json.loads((tmp_path / "result.json").read_text())
    assert meta["min_cx"] == 10
    assert meta["max_cx"] == 12
    assert meta["min_cz"] == -5
    assert meta["max_cz"] == -3
    assert meta["cols"] == 3
    assert meta["rows"] == 3
    assert meta["total"] == 2
    assert meta["delete"] == 1
    assert meta["keep"] == 1
    assert meta["query"] == "InhabitedTime < 120"
    assert meta["dimension"] == "overworld"
    assert "timestamp" in meta


def test_multi_dimension_metadata_dimension_key(tmp_path):
    """Each dimension's JSON metadata records the correct dimension name."""
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
    generate_raw_file(dimensions, query="q", output_path=out)
    ow_meta = json.loads((tmp_path / "migration-overworld.json").read_text())
    nether_meta = json.loads((tmp_path / "migration-nether.json").read_text())
    assert ow_meta["dimension"] == "overworld"
    assert nether_meta["dimension"] == "nether"
