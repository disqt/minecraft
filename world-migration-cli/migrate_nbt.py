"""Minimal NBT tag reader — extracts DataVersion and InhabitedTime from chunk data."""

import gzip
import io
import math
import struct
import zlib

# NBT tag type IDs
_TAG_END = 0
_TAG_BYTE = 1
_TAG_SHORT = 2
_TAG_INT = 3
_TAG_LONG = 4
_TAG_FLOAT = 5
_TAG_DOUBLE = 6
_TAG_BYTE_ARRAY = 7
_TAG_STRING = 8
_TAG_LIST = 9
_TAG_COMPOUND = 10
_TAG_INT_ARRAY = 11
_TAG_LONG_ARRAY = 12

# Fixed payload sizes in bytes (0 = variable)
_FIXED_SIZE = {
    _TAG_BYTE: 1,
    _TAG_SHORT: 2,
    _TAG_INT: 4,
    _TAG_LONG: 8,
    _TAG_FLOAT: 4,
    _TAG_DOUBLE: 8,
}

# Bytes per element for array types
_ARRAY_ELEM_SIZE = {
    _TAG_BYTE_ARRAY: 1,
    _TAG_INT_ARRAY: 4,
    _TAG_LONG_ARRAY: 8,
}


def _skip_payload(buf: io.BytesIO, tag_id: int) -> None:
    """Advance buf past the payload of a tag whose name has already been consumed."""
    if tag_id in _FIXED_SIZE:
        buf.read(_FIXED_SIZE[tag_id])
    elif tag_id == _TAG_STRING:
        (length,) = struct.unpack(">H", buf.read(2))
        buf.read(length)
    elif tag_id in _ARRAY_ELEM_SIZE:
        (count,) = struct.unpack(">i", buf.read(4))
        buf.read(count * _ARRAY_ELEM_SIZE[tag_id])
    elif tag_id == _TAG_LIST:
        (item_type,) = struct.unpack(">b", buf.read(1))
        (count,) = struct.unpack(">i", buf.read(4))
        if item_type == _TAG_COMPOUND:
            for _ in range(count):
                _skip_compound_body(buf)
        elif item_type in _FIXED_SIZE:
            buf.read(count * _FIXED_SIZE[item_type])
        else:
            # Recurse per item for variable-length list elements
            for _ in range(count):
                _skip_payload(buf, item_type)
    elif tag_id == _TAG_COMPOUND:
        _skip_compound_body(buf)
    # TAG_END has no payload; unknown IDs are silently ignored


def _skip_compound_body(buf: io.BytesIO) -> None:
    """Consume tags until TAG_END."""
    while True:
        type_byte = buf.read(1)
        if not type_byte or type_byte[0] == _TAG_END:
            return
        tag_id = type_byte[0]
        # Skip name
        (name_len,) = struct.unpack(">H", buf.read(2))
        buf.read(name_len)
        _skip_payload(buf, tag_id)


def _read_name(buf: io.BytesIO) -> str:
    (name_len,) = struct.unpack(">H", buf.read(2))
    return buf.read(name_len).decode("utf-8", errors="replace")


def _scan_compound(buf: io.BytesIO) -> dict:
    """
    Walk the immediate children of a compound tag body (name already consumed).
    Returns a dict with keys "DataVersion", "InhabitedTime", and "Level" (as a
    nested dict from recursing into a Level compound, if present).
    Stops as soon as all three targets are found (or TAG_END is hit).
    """
    result: dict = {}
    targets = {"DataVersion", "InhabitedTime", "Level"}

    while True:
        type_byte = buf.read(1)
        if not type_byte or type_byte[0] == _TAG_END:
            break
        tag_id = type_byte[0]
        name = _read_name(buf)

        if name == "DataVersion" and tag_id == _TAG_INT:
            (val,) = struct.unpack(">i", buf.read(4))
            result["DataVersion"] = val
        elif name == "InhabitedTime" and tag_id == _TAG_LONG:
            (val,) = struct.unpack(">q", buf.read(8))
            result["InhabitedTime"] = val
        elif name == "Level" and tag_id == _TAG_COMPOUND:
            result["Level"] = _scan_compound(buf)
        else:
            _skip_payload(buf, tag_id)

        # Early exit once we have everything we need
        if targets.issubset(result) or (
            "DataVersion" in result and "InhabitedTime" in result
        ):
            break

    return result


def extract_chunk_tags(
    compressed_data: bytes,
    compression: int,
) -> dict:
    """
    Decompress chunk data and extract DataVersion and InhabitedTime.

    Args:
        compressed_data: Raw compressed bytes from the region file chunk.
        compression: 1=gzip, 2=zlib, 3=uncompressed, 4=lz4.

    Returns:
        {"DataVersion": int|None, "InhabitedTime": int|None}
        Never raises — returns None values on any error.
    """
    null_result: dict = {"DataVersion": None, "InhabitedTime": None}

    try:
        # Decompress
        if compression == 2:
            raw = zlib.decompress(compressed_data)
        elif compression == 1:
            raw = gzip.decompress(compressed_data)
        elif compression == 3:
            raw = compressed_data
        elif compression == 4:
            try:
                import lz4.frame  # type: ignore
                raw = lz4.frame.decompress(compressed_data)
            except ImportError:
                return null_result
        else:
            return null_result

        buf = io.BytesIO(raw)

        # Root tag must be TAG_COMPOUND
        type_byte = buf.read(1)
        if not type_byte or type_byte[0] != _TAG_COMPOUND:
            return null_result

        # Skip root name (usually empty)
        (name_len,) = struct.unpack(">H", buf.read(2))
        buf.read(name_len)

        # Scan root compound
        root = _scan_compound(buf)

        data_version: int | None = root.get("DataVersion")
        inhabited_time: int | None = root.get("InhabitedTime")

        # Pre-1.18: InhabitedTime lives inside the Level sub-compound
        if inhabited_time is None and "Level" in root:
            inhabited_time = root["Level"].get("InhabitedTime")

        return {
            "DataVersion": data_version,
            "InhabitedTime": inhabited_time,
        }

    except Exception:
        return null_result


def inhabited_bucket(ticks: int) -> int:
    """
    Map InhabitedTime (game ticks) to a 0-5 logarithmic bucket.

    0 = unvisited, 1-5 = increasing familiarity.
    Scale is logarithmic base-5000000 over 4 steps (buckets 1-4), capped at 5.
    """
    if ticks == 0:
        return 0
    return min(5, 1 + int(math.log10(max(1, ticks)) / math.log10(5_000_000) * 5))
