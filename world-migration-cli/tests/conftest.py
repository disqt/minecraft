# tests/conftest.py
import struct
import zlib
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def _nbt_string_prefix(name: str) -> bytes:
    """2-byte big-endian length prefix + UTF-8 name bytes."""
    encoded = name.encode("utf-8")
    return struct.pack(">H", len(encoded)) + encoded


def _nbt_int_tag(name: str, value: int) -> bytes:
    """TAG_INT (3) with name and 4-byte big-endian payload."""
    return b"\x03" + _nbt_string_prefix(name) + struct.pack(">i", value)


def _nbt_long_tag(name: str, value: int) -> bytes:
    """TAG_LONG (4) with name and 8-byte big-endian payload."""
    return b"\x04" + _nbt_string_prefix(name) + struct.pack(">q", value)


def _nbt_compound_tag(name: str, children: bytes) -> bytes:
    """TAG_COMPOUND (10) with name, children bytes, and TAG_END terminator."""
    return b"\x0a" + _nbt_string_prefix(name) + children + b"\x00"


def _build_1_18_nbt() -> bytes:
    """Root compound with DataVersion=3955 and InhabitedTime=500 (MC 1.18+ layout)."""
    children = _nbt_int_tag("DataVersion", 3955) + _nbt_long_tag("InhabitedTime", 500)
    # Root compound: TAG_COMPOUND + empty name (length=0) + children + TAG_END
    return b"\x0a" + struct.pack(">H", 0) + children + b"\x00"


def _build_pre_1_18_nbt() -> bytes:
    """Root compound with DataVersion=2730 and Level sub-compound containing InhabitedTime=12000."""
    level_children = _nbt_long_tag("InhabitedTime", 12000)
    level_compound = _nbt_compound_tag("Level", level_children)
    children = _nbt_int_tag("DataVersion", 2730) + level_compound
    return b"\x0a" + struct.pack(">H", 0) + children + b"\x00"


def pytest_configure(config):
    """Generate binary .mca and .nbt fixtures if they don't exist."""
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

    # r.0.1.mca — all zeros (no chunks)
    path_empty = FIXTURES / "r.0.1.mca"
    if not path_empty.exists():
        path_empty.write_bytes(bytes(8192))

    # chunk_1_18.nbt — zlib-compressed MC 1.18+ chunk (DataVersion=3955, InhabitedTime=500)
    path_1_18 = FIXTURES / "chunk_1_18.nbt"
    if not path_1_18.exists():
        path_1_18.write_bytes(zlib.compress(_build_1_18_nbt()))

    # chunk_pre_1_18.nbt — zlib-compressed pre-1.18 chunk (DataVersion=2730, Level.InhabitedTime=12000)
    path_pre_1_18 = FIXTURES / "chunk_pre_1_18.nbt"
    if not path_pre_1_18.exists():
        path_pre_1_18.write_bytes(zlib.compress(_build_pre_1_18_nbt()))
