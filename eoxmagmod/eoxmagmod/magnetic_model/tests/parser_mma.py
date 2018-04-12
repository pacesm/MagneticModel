#-------------------------------------------------------------------------------
#
#  Swarm MMA_SHA_2C product file format parser
#
# Author: Martin Paces <martin.paces@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2018 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------
# pylint: disable=missing-docstring

from unittest import TestCase, main
from numpy import abs as aabs
from spacepy import pycdf
from eoxmagmod.magnetic_model.parser_mma import read_swarm_mma_2c_file
from eoxmagmod.magnetic_model.tests.data import SWARM_MMA_SHA_2C_TEST_DATA


class TestSwarmMMAParser(TestCase):

    @staticmethod
    def parse(filename):
        with pycdf.CDF(filename) as cdf:
            return read_swarm_mma_2c_file(cdf)

    def _assert_valid(self, coeff_field, data, expected_data):
        tested_data = {
            key: data[key] for key in expected_data
        }
        self.assertEqual(tested_data, expected_data)
        self.assertEqual(data["t"].size, data[coeff_field].shape[1])
        self.assertEqual(data["nm"].shape[0], data[coeff_field].shape[0])
        self.assertEqual(data["nm"].shape[1], 2)
        self.assertEqual(data["nm"][..., 0].min(), data["degree_min"])
        self.assertEqual(data["nm"][..., 0].max(), data["degree_max"])
        self.assertTrue(aabs(data["nm"][..., 1]).max() <= data["degree_max"])

    def test_parse_swarm_mio_file(self):
        data = self.parse(SWARM_MMA_SHA_2C_TEST_DATA)
        self._assert_valid("gh", data["gh"][0], {
            "degree_min": 1,
            "degree_max": 1,
        })
        self._assert_valid("gh", data["gh"][1], {
            "degree_min": 1,
            "degree_max": 3,
        })
        self._assert_valid("qs", data["qs"][0], {
            "degree_min": 1,
            "degree_max": 1,
        })
        self._assert_valid("qs", data["qs"][1], {
            "degree_min": 1,
            "degree_max": 2,
        })


if __name__ == "__main__":
    main()
