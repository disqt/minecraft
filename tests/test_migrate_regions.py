# tests/test_migrate_regions.py
from pathlib import Path
from scripts.migrate_regions import count_chunks_in_region, count_chunks_in_directory

FIXTURES = Path(__file__).parent / "fixtures"


def test_count_chunks_populated_region():
    assert count_chunks_in_region(FIXTURES / "r.0.0.mca") == 5


def test_count_chunks_empty_region():
    assert count_chunks_in_region(FIXTURES / "r.empty.mca") == 0


def test_count_chunks_in_directory(tmp_path):
    import shutil
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    shutil.copy(FIXTURES / "r.0.0.mca", region_dir / "r.0.0.mca")
    shutil.copy(FIXTURES / "r.empty.mca", region_dir / "r.-1.0.mca")
    assert count_chunks_in_directory(region_dir) == 5


def test_count_chunks_nonexistent_dir(tmp_path):
    assert count_chunks_in_directory(tmp_path / "nope") == 0
