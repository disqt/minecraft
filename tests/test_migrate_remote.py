from scripts.migrate_remote import dimension_region_subpath, build_scp_commands


def test_overworld_subpath():
    assert dimension_region_subpath("overworld") == "region"


def test_nether_subpath():
    assert dimension_region_subpath("nether") == "DIM-1/region"


def test_end_subpath():
    assert dimension_region_subpath("end") == "DIM1/region"


def test_build_scp_commands_overworld_only():
    cmds = build_scp_commands(
        host="minecraft",
        remote_path="/home/minecraft/serverfiles/world_new",
        local_path="/tmp/work/world_new",
        dimensions=["overworld"],
    )
    # level.dat + overworld region contents
    assert len(cmds) == 2
    assert any("level.dat" in cmd[1] for cmd in cmds)
    # Overworld: downloads region/* contents into local region/ dir
    region_cmd = [c for c in cmds if "region" in c[1]][0]
    assert "region/*" in region_cmd[0][-2]  # remote source has glob
    assert region_cmd[0][-1].endswith("region")  # local target is the dir


def test_build_scp_commands_all_dimensions():
    cmds = build_scp_commands(
        host="minecraft",
        remote_path="/home/minecraft/serverfiles/world_new",
        local_path="/tmp/work/world_new",
        dimensions=["overworld", "nether", "end"],
    )
    # level.dat + 3 dimension region dirs
    assert len(cmds) == 4
