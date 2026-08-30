# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# netCDF4 - MIT License - https://opensource.org/licenses/MIT
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

"""Tests that `ncompare` can still read netCDF files after it has been imported.

`h5py` and `netCDF4` each bundle their own copy of the HDF5 library, and only the
first one loaded is used. If `h5py` loads first, `netCDF4` can no longer open
valid netCDF4 files. `ncompare/__init__.py` imports `netCDF4` first to prevent
that; these tests are what keep it there.

Every test here runs in a **fresh interpreter**, deliberately. Importing `netCDF4`
anywhere earlier in the process fixes the load order, and `tests/conftest.py` does
exactly that -- so an in-process version of these tests would pass whether or not
the fix is present, and would guard nothing.
"""

import subprocess
import sys

from . import data_for_tests_dir

FILE_A = str(data_for_tests_dir / "test_a.nc")
FILE_B = str(data_for_tests_dir / "test_b.nc")


def _run_in_fresh_interpreter(code: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


def test_netcdf_is_readable_after_importing_ncompare():
    """Importing `ncompare` must not break netCDF4's ability to open a file."""
    result = _run_in_fresh_interpreter(
        "import ncompare\n"
        "import xarray as xr\n"
        f"with xr.open_dataset(r'{FILE_A}', engine='netcdf4') as dataset:\n"
        "    print(sorted(dataset.sizes))\n"
    )
    assert result.returncode == 0, (
        f"Reading a netCDF file failed after importing ncompare.\n{result.stderr}"
    )
    assert "conditions" in result.stdout


def test_compare_works_in_a_fresh_interpreter():
    """`compare()` must work as the first thing a process does, as it does via the CLI."""
    result = _run_in_fresh_interpreter(
        f"from ncompare.core import compare\nprint(compare(r'{FILE_A}', r'{FILE_B}'))\n"
    )
    assert result.returncode == 0, f"compare() failed in a fresh interpreter.\n{result.stderr}"


def test_cli_compares_netcdf_files():
    """End-to-end guard on the CLI, the path that was broken on Linux (see #363)."""
    result = subprocess.run(["ncompare", FILE_A, FILE_B], capture_output=True, text=True)
    assert result.returncode == 0, (
        f"The ncompare CLI failed on netCDF input.\n{result.stdout}\n{result.stderr}"
    )
