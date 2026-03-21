from pathlib import Path
from migrate_remote import (
    detect_local_layout,
    DimensionPaths,
    dimension_region_subpath,
)


def test_overworld_subpath():
    assert dimension_region_subpath("overworld") == "region"


def test_nether_subpath():
    assert dimension_region_subpath("nether") == "DIM-1/region"


def test_end_subpath():
    assert dimension_region_subpath("end") == "DIM1/region"


def test_detect_vanilla_layout(tmp_path):
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    (world / "DIM-1" / "region").mkdir(parents=True)
    (world / "DIM1" / "region").mkdir(parents=True)
    paths = detect_local_layout(world)
    assert paths.overworld == world / "region"
    assert paths.nether == world / "DIM-1" / "region"
    assert paths.end == world / "DIM1" / "region"


def test_detect_papermc_layout(tmp_path):
    root = tmp_path / "serverfiles"
    (root / "world_new" / "region").mkdir(parents=True)
    (root / "world_new_nether" / "DIM-1" / "region").mkdir(parents=True)
    (root / "world_new_the_end" / "DIM1" / "region").mkdir(parents=True)
    paths = detect_local_layout(root / "world_new")
    assert paths.overworld == root / "world_new" / "region"
    assert paths.nether == root / "world_new_nether" / "DIM-1" / "region"
    assert paths.end == root / "world_new_the_end" / "DIM1" / "region"


def test_detect_overworld_only(tmp_path):
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    paths = detect_local_layout(world)
    assert paths.overworld == world / "region"
    assert paths.nether is None
    assert paths.end is None


def test_dimension_paths_available(tmp_path):
    world = tmp_path / "world"
    (world / "region").mkdir(parents=True)
    (world / "DIM-1" / "region").mkdir(parents=True)
    paths = detect_local_layout(world)
    assert set(paths.available_dimensions()) == {"overworld", "nether"}
