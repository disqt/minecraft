"""SSH/SCP operations for downloading Minecraft world files."""

import subprocess
import sys
from pathlib import Path

DIMENSION_SUBPATHS = {
    "overworld": "region",
    "nether": "DIM-1/region",
    "end": "DIM1/region",
}


def dimension_region_subpath(dimension: str) -> str:
    """Return the relative path from world root to the region dir for a dimension."""
    return DIMENSION_SUBPATHS[dimension]


def build_scp_commands(
    host: str,
    remote_path: str,
    local_path: str,
    dimensions: list[str],
) -> list[tuple[list[str], str]]:
    """Build SCP commands to download world files.

    Returns a list of (command_args, description) tuples.
    Downloads region/* contents (not the directory itself) to avoid nested region/region/.
    """
    commands = []

    # Always download level.dat
    commands.append((
        ["scp", f"{host}:{remote_path}/level.dat", f"{local_path}/level.dat"],
        f"level.dat",
    ))

    for dim in dimensions:
        subpath = dimension_region_subpath(dim)
        # Download region/* contents into local region/ dir (not the dir itself)
        remote_region = f"{host}:{remote_path}/{subpath}/*"
        local_region = f"{local_path}/{subpath}"
        commands.append((
            ["scp", "-r", remote_region, local_region],
            f"{dim} region ({subpath})",
        ))

    return commands


def run_scp_commands(
    commands: list[tuple[list[str], str]],
    local_path: Path,
) -> None:
    """Execute SCP commands, creating local directories as needed."""
    for cmd_args, description in commands:
        # Ensure parent directory exists for the target
        target = Path(cmd_args[-1])
        target.parent.mkdir(parents=True, exist_ok=True)

        print(f"  Downloading {description}...", file=sys.stderr)
        result = subprocess.run(cmd_args, capture_output=True, text=True)
        if result.returncode != 0:
            print(
                f"ERROR: SCP failed for {description}: {result.stderr}",
                file=sys.stderr,
            )
            sys.exit(3)


def check_ssh_connectivity(host: str) -> bool:
    """Test SSH connectivity to the host. Returns True if reachable."""
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", host, "echo ok"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and "ok" in result.stdout
