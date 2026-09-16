from __future__ import annotations

from typing import Any, Iterable

import numpy as np


POINT_FIELD_DTYPES = {
    1: np.int8,
    2: np.uint8,
    3: np.int16,
    4: np.uint16,
    5: np.int32,
    6: np.uint32,
    7: np.float32,
    8: np.float64,
}


def _structured_dtype(fields: Iterable[Any], point_step: int, big_endian: bool) -> np.dtype:
    names: list[str] = []
    formats: list[np.dtype] = []
    offsets: list[int] = []
    byte_order = ">" if big_endian else "<"

    for field in fields:
        if field.datatype not in POINT_FIELD_DTYPES:
            continue
        base = np.dtype(POINT_FIELD_DTYPES[field.datatype]).newbyteorder(byte_order)
        count = int(field.count)
        names.append(str(field.name))
        formats.append(base if count == 1 else np.dtype((base, count)))
        offsets.append(int(field.offset))

    return np.dtype(
        {"names": names, "formats": formats, "offsets": offsets, "itemsize": int(point_step)}
    )


def pointcloud2_xyz(message: Any) -> np.ndarray:
    """Decode x/y/z fields from a SDK PointCloud2_ compatible object."""
    dtype = _structured_dtype(message.fields, message.point_step, message.is_bigendian)
    required = {"x", "y", "z"}
    if not required.issubset(dtype.names or ()):
        raise ValueError(f"Point cloud must contain x/y/z fields, got {dtype.names}")

    raw = bytes(message.data)
    expected_points = int(message.width) * int(message.height)
    available_points = len(raw) // int(message.point_step)
    count = min(expected_points, available_points)
    records = np.frombuffer(raw, dtype=dtype, count=count)
    points = np.column_stack((records["x"], records["y"], records["z"])).astype(
        np.float32, copy=False
    )
    return points[np.isfinite(points).all(axis=1)]

