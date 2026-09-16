import struct
import unittest
from types import SimpleNamespace

import numpy as np

from go2_module1.pointcloud import pointcloud2_xyz


class PointCloudTest(unittest.TestCase):
    def test_decodes_xyz(self) -> None:
        fields = [
            SimpleNamespace(name="x", offset=0, datatype=7, count=1),
            SimpleNamespace(name="y", offset=4, datatype=7, count=1),
            SimpleNamespace(name="z", offset=8, datatype=7, count=1),
            SimpleNamespace(name="intensity", offset=12, datatype=7, count=1),
        ]
        data = b"".join(struct.pack("<ffff", *point) for point in [(1, 2, 3, 9), (4, 5, 6, 8)])
        message = SimpleNamespace(
            fields=fields,
            point_step=16,
            is_bigendian=False,
            data=data,
            width=2,
            height=1,
        )
        np.testing.assert_allclose(pointcloud2_xyz(message), [[1, 2, 3], [4, 5, 6]])


if __name__ == "__main__":
    unittest.main()

