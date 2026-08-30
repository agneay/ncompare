# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# colorama - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# netCDF4 - MIT License - https://opensource.org/licenses/MIT
# numpy - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
# openpyxl - MIT License - https://opensource.org/licenses/MIT
# xarray - Apache License, version 2.0 - https://www.apache.org/licenses/LICENSE-2.0
# Python Standard Library - Python Software Foundation (PSF) License Agreement-
#   https://docs.python.org/3/license.html#psf-license
#
# The ncompare: NetCDF structural comparison tool platform is licensed under the
# Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Main code for comparing NetCDF files."""

from importlib.metadata import version

# `netCDF4` must be imported before `h5py`. Both distribute wheels that bundle
# their own copy of the HDF5 library, and only the first one loaded is used. When
# `h5py` wins that race, `netCDF4` can no longer open valid netCDF4 files on
# Linux, failing with "[Errno -101] NetCDF: HDF error". See
# https://github.com/Unidata/netcdf4-python/issues/653 and
# https://github.com/Unidata/netcdf4-python/issues/1343; importing `netCDF4`
# first is the accepted workaround.
#
# Importing it here fixes the order for every entry point, because Python runs
# this module before any `ncompare` submodule. It cannot be fixed by reordering
# the imports inside those submodules: `h5py` sorts before `netCDF4`
# alphabetically, so the linter would just put it back.
#
# tests/test_import_order.py guards this.
import netCDF4  # noqa: F401  # imported first for its side effect on load order

from .core import (
    compare,
)

__all__ = [
    "compare",
]

__version__ = version("ncompare")
