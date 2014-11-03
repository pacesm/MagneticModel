#-------------------------------------------------------------------------------
#
#  Magnetic Model
#
# Project: Earth magnetic field in Python.
# Author: Martin Paces <martin.paces@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2014 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all
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

import os.path
import numpy as np

# location of the data files
dirname = os.path.dirname(__file__)
DATA_WMM_2010 = os.path.join(dirname, 'data/WMM.COF')
DATA_EMM_2010_STATIC = os.path.join(dirname, 'data/EMM-720_V3p0_static.cof')
DATA_EMM_2010_SECVAR = os.path.join(dirname, 'data/EMM-720_V3p0_secvar.cof')

# coordinate systems and their trasnformation
from _pywmm import (
    GEODETIC_ABOVE_WGS84, GEODETIC_ABOVE_EGM96,
    GEOCENTRIC_SPHERICAL, GEOCENTRIC_CARTESIAN,
    POTENTIAL, GRADIENT, POTENTIAL_AND_GRADIENT,
    convert, legendre, lonsincos, relradpow, spharpot, sphargrd,
    vrot_sph2geod, vrot_sph2cart, geomag,
)

COORD_TYPES = (
    (GEODETIC_ABOVE_WGS84, "GEODETIC_ABOVE_WGS84"),
    (GEODETIC_ABOVE_EGM96, "GEODETIC_ABOVE_EGM96"),
    (GEOCENTRIC_SPHERICAL, "GEOCENTRIC_SPHERICAL"),
    (GEOCENTRIC_CARTESIAN, "GEOCENTRIC_CARTESIAN"),
)

EVAL_MODES = (
    (POTENTIAL, "POTENTIAL"),
    (GRADIENT, "GRADIENT"),
    (POTENTIAL_AND_GRADIENT, "POTENTIAL_AND_GRADIENT"),
)

def vnorm(arr):
    """Calculate norms for each vector form an input array of vectors."""
    return np.sqrt((arr*arr).sum(axis=arr.ndim-1))


class MagneticModel(object):
    """ Base Magnetic model class """

    def __init__(self, model_prm):
        """ Model constructor """
        self.prm = model_prm

    @property
    def validity(self):
        """Get interval of model validity."""
        raise NotImplementedError

    def is_valid_date(self, date):
        """Check whether the date is within the interval of validity."""
        vrange = self.validity
        return (date >= vrange[0]) and (date <= vrange[1])

    @property
    def degree_static(self):
        """Get the degree of the static model."""
        raise NotImplementedError

    @property
    def degree_secvar(self):
        """Get the degree of the secular variation model."""
        raise NotImplementedError

    def get_coef_static(self, date):
        """ Calculate model static coeficients for a date specified by a decimal year value.
        """
        raise NotImplementedError

    def get_coef_secvar(self, date):
        """Get secular variation coeficients."""
        raise NotImplementedError

    def print_info(self):
        """Print information about the model."""
        print self


    def eval(self, arr_in, date, coord_type_in=GEODETIC_ABOVE_WGS84,
                coord_type_out=None, secvar=False, mode=GRADIENT, maxdegree=-1,
                check_date_validity=True):
        """Evaluate spherical harmonic model for a given set of spatio-teporal
        coordinates.

        Input:
            model - an instance of the MagneticModel class
            arr_in - numpy array of (x, y, z) coordinates.
                     The type of the x, y, z, values depends on the selected
                     input coordinate system.

            date - The time as a decimal year value (e.g., 2015.23).
            coord_type_in - shall be set to one of the valid coordinate systems:
                        GEODETIC_ABOVE_WGS84 (default)
                        GEODETIC_ABOVE_EGM96
                        GEOCENTRIC_SPHERICAL
                        GEOCENTRIC_CARTESIAN

            coord_type_out - coordinate system of the output vector
                        GEODETIC_ABOVE_WGS84
                        GEODETIC_ABOVE_EGM96 (the same as WGS84)
                        GEOCENTRIC_SPHERICAL
                        GEOCENTRIC_CARTESIAN
                    Ouput coordinate system defaults to the input coordinate
                    system.

            secvar - if True secular variation of the magentic field is
                     calculated rather than the magnetic fied.

            mode - type of output to be produced. The possible values are:
                        POTENTIAL
                        GRADIENT (default)
                        POTENTIAL_AND_GRADIENT

            maxdegree - an optional max. allowed modelel degree
                    (i.e., truncated evaluation). If set to -1 no limit
                    is imposed.

            check_date_validity - boolean flag controlling  whether the date
                    vality will is checked (True, by default) or not (False).

        Output:

            arr_out - output numpy array with the same shape as the input
                      array contaning the calcuated magentic field parameters.
        """
        if mode not in dict(EVAL_MODES):
            raise ValueError("Invalid mode value!")

        if coord_type_in not in dict(COORD_TYPES):
            raise ValueError("Invalid input coordinate type!")

        if coord_type_out is None:
            coord_type_out = coord_type_in

        if coord_type_out not in dict(COORD_TYPES):
            raise ValueError("Invalid output coordinate type!")

        if check_date_validity and not self.is_valid_date(date):
            raise ValueError("The date is outside of the model validity range!")

        if secvar:
            degree = self.degree_secvar
            coef_g, coef_h = self.get_coef_secvar(date)
        else:
            degree = self.degree_static
            coef_g, coef_h = self.get_coef_static(date)

        if maxdegree > 0:
            degree = min(maxdegree, degree)

        return geomag(arr_in, degree, coef_g, coef_h, coord_type_in, coord_type_out, mode)
