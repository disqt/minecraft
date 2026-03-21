# tests/test_migrate_nbt.py
from pathlib import Path

from migrate_nbt import extract_chunk_tags, inhabited_bucket

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_1_18_chunk():
    compressed = (FIXTURES / "chunk_1_18.nbt").read_bytes()
    tags = extract_chunk_tags(compressed, compression=2)
    assert tags["DataVersion"] == 3955
    assert tags["InhabitedTime"] == 500


def test_extract_pre_1_18_chunk():
    compressed = (FIXTURES / "chunk_pre_1_18.nbt").read_bytes()
    tags = extract_chunk_tags(compressed, compression=2)
    assert tags["DataVersion"] == 2730
    assert tags["InhabitedTime"] == 12000


def test_extract_handles_lz4_gracefully():
    tags = extract_chunk_tags(b"\x00" * 100, compression=4)
    assert tags is not None  # Never crashes


def test_inhabited_bucket_zero():
    assert inhabited_bucket(0) == 0


def test_inhabited_bucket_ranges():
    assert inhabited_bucket(1) == 1
    assert inhabited_bucket(100) == 2
    assert inhabited_bucket(5000) == 3
    assert inhabited_bucket(100000) == 4
    assert inhabited_bucket(5000000) == 5
