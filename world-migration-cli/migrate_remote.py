"""World resolution — local layout detection and SSH download."""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# Compat: migrate_mca.py imports this for MCA Selector --region flag building
DIMENSION_SUBPATHS = {
    "overworld": "region",
    "nether": "DIM-1/region",
    "end": "DIM1/region",
}


def dimension_region_subpath(dimension: str) -> str:
    """Return relative path from world root to region dir (Vanilla layout)."""
    return DIMENSION_SUBPATHS[dimension]


@dataclass
class DimensionPaths:
    """Resolved paths to each dimension's region directory."""
    overworld: Path | None = None
    nether: Path | None = None
    end: Path | None = None

    def available_dimensions(self, check_filesystem: bool = True) -> list[str]:
        """Return list of dimensions that have paths set.
        If check_filesystem=True, also verifies dirs exist locally.
        Set check_filesystem=False for remote layouts where paths are relative.
        """
        dims = []
        for name, path in [("overworld", self.overworld), ("nether", self.nether), ("end", self.end)]:
            if path is None:
                continue
            if check_filesystem and not path.is_dir():
                continue
            dims.append(name)
        return dims

    def region_dir(self, dimension: str) -> Path | None:
        return {"overworld": self.overworld, "nether": self.nether, "end": self.end}[dimension]


def detect_local_layout(world_path: Path) -> DimensionPaths:
    """Detect whether a local world uses Vanilla or PaperMC dimension layout."""
    paths = DimensionPaths()

    # Overworld
    ow_region = world_path / "region"
    if ow_region.is_dir():
        paths.overworld = ow_region

    # Vanilla nether/end first
    vanilla_nether = world_path / "DIM-1" / "region"
    vanilla_end = world_path / "DIM1" / "region"
    if vanilla_nether.is_dir():
        paths.nether = vanilla_nether
    if vanilla_end.is_dir():
        paths.end = vanilla_end

    # PaperMC fallback (sibling dirs)
    if paths.nether is None:
        parent = world_path.parent
        paper_nether = parent / f"{world_path.name}_nether" / "DIM-1" / "region"
        if paper_nether.is_dir():
            paths.nether = paper_nether

    if paths.end is None:
        parent = world_path.parent
        paper_end = parent / f"{world_path.name}_the_end" / "DIM1" / "region"
        if paper_end.is_dir():
            paths.end = paper_end

    return paths


def detect_remote_layout(host: str, remote_world_path: str) -> DimensionPaths:
    """Detect whether a remote world uses Vanilla or PaperMC dimension layout via SSH."""
    paths = DimensionPaths()

    def remote_dir_exists(path: str) -> bool:
        result = subprocess.run(
            ["ssh", host, f"test -d {path}"],
            capture_output=True,
        )
        return result.returncode == 0

    # Overworld
    ow_region = f"{remote_world_path}/region"
    if remote_dir_exists(ow_region):
        paths.overworld = Path(ow_region)

    # Vanilla nether/end first
    vanilla_nether = f"{remote_world_path}/DIM-1/region"
    vanilla_end = f"{remote_world_path}/DIM1/region"
    if remote_dir_exists(vanilla_nether):
        paths.nether = Path(vanilla_nether)
    if remote_dir_exists(vanilla_end):
        paths.end = Path(vanilla_end)

    # PaperMC fallback (sibling dirs)
    posix = PurePosixPath(remote_world_path)
    world_name = posix.name
    parent = str(posix.parent)

    if paths.nether is None:
        paper_nether = f"{parent}/{world_name}_nether/DIM-1/region"
        if remote_dir_exists(paper_nether):
            paths.nether = Path(paper_nether)

    if paths.end is None:
        paper_end = f"{parent}/{world_name}_the_end/DIM1/region"
        if remote_dir_exists(paper_end):
            paths.end = Path(paper_end)

    return paths


def _scp(host: str, remote_src: str, local_dst: Path) -> None:
    """Download a single file via SCP."""
    local_dst.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["scp", f"{host}:{remote_src}", str(local_dst)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: SCP failed for {remote_src}: {result.stderr}", file=sys.stderr)
        sys.exit(3)


def _scp_recursive(host: str, remote_src_glob: str, local_dst: Path) -> None:
    """Download remote files matching a glob into a local directory via SCP."""
    local_dst.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["scp", "-r", f"{host}:{remote_src_glob}", str(local_dst)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: SCP failed for {remote_src_glob}: {result.stderr}", file=sys.stderr)
        sys.exit(3)


def download_world(
    host: str,
    remote_paths: DimensionPaths,
    local_world: Path,
    remote_world_root: str,
) -> None:
    """Download world files from a remote server using detected DimensionPaths.

    Downloads level.dat from remote_world_root, then each dimension's region
    directory contents into the corresponding local path.
    """
    # Download level.dat from the remote world root
    print("  Downloading level.dat...", file=sys.stderr)
    _scp(host, f"{remote_world_root}/level.dat", local_world / "level.dat")

    # Download each available dimension's region files
    dim_map = [
        ("overworld", remote_paths.overworld),
        ("nether", remote_paths.nether),
        ("end", remote_paths.end),
    ]
    for dim_name, remote_region_path in dim_map:
        if remote_region_path is None:
            continue

        # Compute local destination: mirror the subpath under local_world
        subpath = dimension_region_subpath(dim_name)
        local_region = local_world / subpath
        print(f"  Downloading {dim_name} region ({subpath})...", file=sys.stderr)
        _scp_recursive(host, f"{remote_region_path}/*", local_region)
