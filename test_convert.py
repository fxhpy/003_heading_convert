import unittest

import numpy as np

from step03_convert_direction import interpolate_direction, relative_wave_direction

class DirectionTests(unittest.TestCase):
    def test_direction_crosses_zero(self):
        result = interpolate_direction(
            np.array([0.0, 3600.0]),
            np.array([359.0, 1.0]),
            np.array([1800.0]),
        )
        self.assertTrue(result[0] < 0.01 or result[0] > 359.99)

    def test_relative_direction(self):
        relative_360, relative_signed = relative_wave_direction(
            np.array([10.0, 350.0]),
            np.array([350.0, 10.0]),
        )
        np.testing.assert_allclose(relative_360, [20.0, 340.0])
        np.testing.assert_allclose(relative_signed, [20.0, -20.0])

if __name__ == "__main__":
    unittest.main()
