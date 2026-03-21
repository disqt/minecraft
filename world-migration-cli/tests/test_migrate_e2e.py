# tests/test_migrate_e2e.py
"""End-to-end pipeline tests for the migration tool."""

import json
import struct
from pathlib import Path

from tests.test_migrate_regions import make_region_with_chunks


def setup_world(tmp_path, chunks=None):
    """Create minimal Vanilla-layout world."""
    if chunks is None:
        chunks = [
            {"slot": 0, "inhabited_time": 500, "data_version": 3955},
            {"slot": 1, "inhabited_time": 50, "data_version": 3955},
            {"slot": 2, "inhabited_time": 0, "data_version": 3955},
        ]
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    make_region_with_chunks(world / "region" / "r.0.0.mca", chunks)
    (world / "level.dat").write_bytes(b"\x00" * 16)
    return world


def test_full_pipeline_html(tmp_path):
    world = setup_world(tmp_path)
    html_out = tmp_path / "preview.html"
    from migrate import run_pipeline, parse_args

    args = parse_args([str(world), "--threshold", "120", "--html", str(html_out)])
    code = run_pipeline(args)
    assert code == 0
    assert html_out.exists()
    content = html_out.read_text()
    assert "Migration Preview" in content
    assert "Overworld" in content


def test_full_pipeline_raw(tmp_path):
    world = setup_world(tmp_path)
    raw_out = tmp_path / "migration.bin"
    from migrate import run_pipeline, parse_args

    args = parse_args([str(world), "--threshold", "120", "--raw", str(raw_out)])
    code = run_pipeline(args)
    assert code == 0
    assert raw_out.exists()
    meta_path = tmp_path / "migration.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text())
    assert meta["total"] == 3
    assert meta["delete"] == 2


def test_full_pipeline_stats_only(tmp_path, capsys):
    world = setup_world(tmp_path)
    from migrate import run_pipeline, parse_args

    args = parse_args([str(world), "--threshold", "120"])
    code = run_pipeline(args)
    assert code == 0
    captured = capsys.readouterr()
    assert "Overworld" in captured.err


def test_trim_actually_deletes_chunks(tmp_path):
    world = setup_world(tmp_path, [
        {"slot": 0, "inhabited_time": 500, "data_version": 3955},
        {"slot": 1, "inhabited_time": 50, "data_version": 3955},
        {"slot": 2, "inhabited_time": 0, "data_version": 3955},
    ])
    from migrate import run_pipeline, parse_args

    args = parse_args([
        str(world), "--threshold", "120", "--dangerously-perform-the-trim",
    ])
    code = run_pipeline(args)
    assert code == 0
    mca = world / "region" / "r.0.0.mca"
    data = mca.read_bytes()
    assert struct.unpack_from(">I", data, 0)[0] != 0  # slot 0: kept
    assert struct.unpack_from(">I", data, 4)[0] == 0   # slot 1: zeroed
    assert struct.unpack_from(">I", data, 8)[0] == 0   # slot 2: zeroed


def test_safety_abort_blocks_trim(tmp_path):
    world = setup_world(tmp_path, [
        {"slot": i, "inhabited_time": 0, "data_version": 3955} for i in range(10)
    ])
    html_out = tmp_path / "preview.html"
    from migrate import run_pipeline, parse_args

    args = parse_args([
        str(world), "--threshold", "120",
        "--html", str(html_out),
        "--dangerously-perform-the-trim",
    ])
    code = run_pipeline(args)
    assert code == 1  # safety abort
    assert html_out.exists()  # HTML still generated
