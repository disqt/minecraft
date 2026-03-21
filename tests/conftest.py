# tests/conftest.py
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    """Generate binary .mca fixtures if they don't exist."""
    FIXTURES.mkdir(exist_ok=True)

    # r.0.0.mca — 5 populated chunks out of 1024
    path_5 = FIXTURES / "r.0.0.mca"
    if not path_5.exists():
        header = bytearray(8192)
        for i in range(5):
            offset = 4 * i
            header[offset + 2] = 1  # non-zero offset byte
            header[offset + 3] = 1  # sector count
        path_5.write_bytes(bytes(header))

    # r.empty.mca — all zeros (no chunks)
    path_empty = FIXTURES / "r.empty.mca"
    if not path_empty.exists():
        path_empty.write_bytes(bytes(8192))
