import pytest
from migrate import parse_args


def test_local_world_with_threshold():
    args = parse_args(["./world", "--threshold", "120", "--html", "out.html"])
    assert args.world_path == "./world"
    assert args.threshold == 120
    assert args.query is None
    assert args.html == "out.html"


def test_ssh_download():
    args = parse_args([
        "--host", "minecraft", "--remote-path", "/home/minecraft/serverfiles",
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
        "./world", "--query", "InhabitedTime < 600 AND DataVersion < 2860",
        "--mcaselector", "./mca.jar", "--html", "out.html",
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
            "./world", "--host", "mc", "--remote-path", "/world", "--html", "out.html",
        ])


def test_dimensions_default_not_set():
    args = parse_args(["./world", "--html", "out.html"])
    assert args.dimensions is None


def test_dimensions_explicit():
    args = parse_args(["./world", "--dimensions", "overworld", "nether", "--html", "out.html"])
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
