"""Tests for modpack_release.py -- pure logic only, no SSH/VPS needed."""

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from modpack_release import (
    extract_mod_version,
    generate_changelog,
    get_local_mod_list,
    load_config,
    load_packignore,
    should_exclude,
    validate_instance,
    zip_instance,
)


# --- extract_mod_version ---


@pytest.mark.parametrize(
    "jar_name, expected",
    [
        ("sodium-fabric-0.6.14+mc1.21.11.jar", ("sodium-fabric", "0.6.14+mc1.21.11")),
        ("lithium-fabric-0.15.1+mc1.21.11.jar", ("lithium-fabric", "0.15.1+mc1.21.11")),
        ("iris-2.0.2+1.21.11.jar", ("iris", "2.0.2+1.21.11")),
        ("owo-lib-0.13.0+1.21.11.jar", ("owo-lib", "0.13.0+1.21.11")),
        ("disquests-client-0.4.0.jar", ("disquests-client", "0.4.0")),
        ("ModName_1.2.3.jar", ("ModName", "1.2.3")),
        ("noversion.jar", ("noversion", "")),
        ("Drip Sounds-0.5.2+1.21.10-Fabric.jar", ("Drip Sounds", "0.5.2+1.21.10-Fabric")),
        ("AutoWalk-1.0,1.21.11.jar.disabled", ("AutoWalk", "1.0,1.21.11")),
    ],
)
def test_extract_mod_version(jar_name, expected):
    assert extract_mod_version(jar_name) == expected


# --- should_exclude ---


def test_should_exclude_exact_match():
    assert should_exclude(".minecraft/logs", [".minecraft/logs"])


def test_should_exclude_subpath():
    assert should_exclude(".minecraft/logs/latest.log", [".minecraft/logs"])


def test_should_exclude_no_match():
    assert not should_exclude(".minecraft/mods/sodium.jar", [".minecraft/logs"])


def test_should_exclude_backslash_normalization():
    assert should_exclude(".minecraft/saves/world1", [".minecraft\\saves"])


def test_should_exclude_multiple_patterns():
    patterns = [".minecraft/logs", ".minecraft/saves", ".minecraft/screenshots"]
    assert should_exclude(".minecraft/saves/world", patterns)
    assert not should_exclude(".minecraft/mods/mod.jar", patterns)


# --- load_packignore ---


def test_load_packignore_missing_file(tmp_path):
    assert load_packignore(tmp_path) == []


def test_load_packignore_reads_patterns(tmp_path):
    (tmp_path / ".packignore").write_text(
        ".minecraft/logs\n.minecraft/saves\n\n  .minecraft/screenshots  \n"
    )
    patterns = load_packignore(tmp_path)
    assert patterns == [".minecraft/logs", ".minecraft/saves", ".minecraft/screenshots"]


# --- load_config ---


def test_load_config(tmp_path):
    cfg = {"vps_host": "dev", "mc_version": "1.21.11", "keep": 3}
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg))
    assert load_config(cfg_path) == cfg


# --- validate_instance ---


def test_validate_instance_not_a_dir(tmp_path):
    with pytest.raises(SystemExit):
        validate_instance(tmp_path / "nonexistent")


def test_validate_instance_no_mmc_pack(tmp_path):
    with pytest.raises(SystemExit):
        validate_instance(tmp_path)


def test_validate_instance_no_mods_dir(tmp_path):
    (tmp_path / "mmc-pack.json").write_text("{}")
    with pytest.raises(SystemExit):
        validate_instance(tmp_path)


def test_validate_instance_ok(tmp_path):
    (tmp_path / "mmc-pack.json").write_text("{}")
    (tmp_path / ".minecraft" / "mods").mkdir(parents=True)
    validate_instance(tmp_path)  # should not raise


# --- zip_instance ---


def _make_instance(tmp_path):
    """Create a minimal fake Prism instance."""
    inst = tmp_path / "instance"
    (inst / ".minecraft" / "mods").mkdir(parents=True)
    (inst / ".minecraft" / "mods" / "sodium.jar").write_bytes(b"fake jar")
    (inst / ".minecraft" / "config" / "sodium.toml").parent.mkdir(parents=True)
    (inst / ".minecraft" / "config" / "sodium.toml").write_text("key=val")
    (inst / ".minecraft" / "logs").mkdir(parents=True)
    (inst / ".minecraft" / "logs" / "latest.log").write_text("log data")
    (inst / ".minecraft" / "saves" / "world").mkdir(parents=True)
    (inst / ".minecraft" / "saves" / "world" / "level.dat").write_bytes(b"world")
    (inst / "mmc-pack.json").write_text("{}")
    (inst / "instance.cfg").write_text("name=test")
    return inst


def test_zip_instance_includes_mods(tmp_path):
    inst = _make_instance(tmp_path)
    out = tmp_path / "out.zip"
    zip_instance(inst, out, "test")
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert "test/.minecraft/mods/sodium.jar" in names
    assert "test/mmc-pack.json" in names


def test_zip_instance_respects_packignore(tmp_path):
    inst = _make_instance(tmp_path)
    (inst / ".packignore").write_text(".minecraft/logs\n.minecraft/saves\n")
    out = tmp_path / "out.zip"
    zip_instance(inst, out, "test")
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert "test/.minecraft/mods/sodium.jar" in names
    assert not any("logs/" in n for n in names)
    assert not any("saves/" in n for n in names)


def test_zip_instance_no_packignore_includes_everything(tmp_path):
    inst = _make_instance(tmp_path)
    out = tmp_path / "out.zip"
    zip_instance(inst, out, "test")
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert any("logs/" in n for n in names)
    assert any("saves/" in n for n in names)


# --- get_local_mod_list ---


def test_get_local_mod_list(tmp_path):
    inst = _make_instance(tmp_path)
    mods_dir = inst / ".minecraft" / "mods"
    (mods_dir / "lithium-0.15.jar").write_bytes(b"jar")
    (mods_dir / "readme.txt").write_text("not a mod")
    (mods_dir / "disabled.jar.disabled").write_text("disabled")
    result = get_local_mod_list(inst)
    assert "sodium.jar" in result
    assert "lithium-0.15.jar" in result
    assert "readme.txt" not in result
    assert "disabled.jar.disabled" not in result


# --- generate_changelog (mocked SSH) ---


def _mock_config():
    return {
        "vps_host": "dev",
        "vps_path": "/home/dev/prism",
        "mc_version": "1.21.11",
        "modloader": "Fabric",
        "disquests_repo": "disqt/disquests",
    }


def test_changelog_initial_release(tmp_path):
    """No previous mods on VPS -> initial release."""
    inst = _make_instance(tmp_path)
    config = _mock_config()
    with patch("modpack_release.get_previous_zip_contents", return_value=(set(), set())):
        changelog = generate_changelog(inst, config)
    assert changelog == ["Initial release"]


def test_changelog_detects_added_mod(tmp_path):
    inst = _make_instance(tmp_path)
    (inst / ".minecraft" / "mods" / "newmod-1.0.jar").write_bytes(b"jar")
    config = _mock_config()
    old_jars = {"sodium-0.6.14.jar"}
    with patch("modpack_release.get_previous_zip_contents", return_value=(old_jars, set())):
        with patch("modpack_release.get_disquests_changelog", return_value=[]):
            changelog = generate_changelog(inst, config)
    assert any("Added newmod" in line for line in changelog)


def test_changelog_detects_removed_mod(tmp_path):
    inst = _make_instance(tmp_path)
    config = _mock_config()
    old_jars = {"sodium.jar", "removed-mod-2.0.jar"}
    with patch("modpack_release.get_previous_zip_contents", return_value=(old_jars, set())):
        with patch("modpack_release.get_disquests_changelog", return_value=[]):
            changelog = generate_changelog(inst, config)
    assert any("Removed removed-mod-2.0.jar" in line for line in changelog)


def test_changelog_detects_updated_mod(tmp_path):
    inst = _make_instance(tmp_path)
    mods = inst / ".minecraft" / "mods"
    (mods / "sodium.jar").unlink()
    (mods / "sodium-0.6.15.jar").write_bytes(b"new")
    config = _mock_config()
    old_jars = {"sodium-0.6.14.jar"}
    with patch("modpack_release.get_previous_zip_contents", return_value=(old_jars, set())):
        with patch("modpack_release.get_disquests_changelog", return_value=[]):
            changelog = generate_changelog(inst, config)
    assert any("Updated" in line and "0.6.14" in line and "0.6.15" in line for line in changelog)
