from pathlib import Path
from migrate_mca import build_select_command, build_delete_command, count_selected_chunks


def test_build_select_overworld(tmp_path):
    jar = tmp_path / "mcaselector.jar"
    world = tmp_path / "world_new"
    csv = tmp_path / "selection-overworld.csv"
    cmd = build_select_command(
        mcaselector_jar=jar, world_dir=world,
        dimension="overworld", query="InhabitedTime < 120",
        output_csv=csv,
    )
    assert cmd[0] == "java"
    assert "-jar" in cmd
    assert str(jar) == cmd[cmd.index("-jar") + 1]
    assert "--mode" in cmd
    assert "select" in cmd
    assert "--query" in cmd
    assert "InhabitedTime < 120" in cmd
    # Overworld should NOT have --region flag
    assert "--region" not in cmd


def test_build_select_nether_uses_region_flag(tmp_path):
    jar = tmp_path / "mcaselector.jar"
    world = tmp_path / "world_new"
    csv = tmp_path / "selection-nether.csv"
    cmd = build_select_command(
        mcaselector_jar=jar, world_dir=world,
        dimension="nether", query="InhabitedTime < 120",
        output_csv=csv,
    )
    assert "--region" in cmd
    region_path = Path(cmd[cmd.index("--region") + 1])
    assert region_path == world / "DIM-1" / "region"


def test_build_delete_overworld(tmp_path):
    jar = tmp_path / "mcaselector.jar"
    world = tmp_path / "world_new"
    cmd = build_delete_command(
        mcaselector_jar=jar, world_dir=world,
        dimension="overworld", query="InhabitedTime < 120",
    )
    assert "delete" in cmd
    assert "--region" not in cmd


def test_build_delete_end_uses_region_flag(tmp_path):
    jar = tmp_path / "mcaselector.jar"
    world = tmp_path / "world_new"
    cmd = build_delete_command(
        mcaselector_jar=jar, world_dir=world,
        dimension="end", query="InhabitedTime < 120",
    )
    assert "--region" in cmd
    region_path = Path(cmd[cmd.index("--region") + 1])
    assert region_path == world / "DIM1" / "region"


def test_count_selected_chunks_nonexistent(tmp_path):
    assert count_selected_chunks(tmp_path / "nope.csv") == 0


def test_count_selected_chunks_empty(tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("")
    assert count_selected_chunks(csv) == 0


def test_count_selected_chunks_with_entries(tmp_path):
    csv = tmp_path / "sel.csv"
    csv.write_text("0;0\n1;0\n2;0\n")
    assert count_selected_chunks(csv) == 3
