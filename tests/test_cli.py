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

import os
import subprocess

from ncompare.console import _cli

from . import data_for_tests_dir


def test_console_version():
    exit_status = os.system("ncompare --version")
    assert exit_status == 0


def test_console_help():
    exit_status = os.system("ncompare --help")
    assert exit_status == 0


def test_arg_parser():
    parsed = _cli(["first_netcdf.nc", "second_netcdf.nc"])

    assert getattr(parsed, "path_a") == "first_netcdf.nc"
    assert getattr(parsed, "path_b") == "second_netcdf.nc"
    assert getattr(parsed, "show_attributes") is False
    assert getattr(parsed, "show_chunks") is False
    assert getattr(parsed, "only_diffs") is False
    assert getattr(parsed, "exit_code") is False


def test_arg_parser_exit_code_flag():
    assert _cli(["first_netcdf.nc", "second_netcdf.nc"]).exit_code is False
    assert _cli(["first_netcdf.nc", "second_netcdf.nc", "--exit-code"]).exit_code is True


def _exit_status(command: str) -> int:
    """Return the exit code of a shell command, decoded from os.system().

    Output is discarded: these tests assert on the exit code, and the failure
    cases would otherwise print full tracebacks into the test log.
    """
    # os.system encodes the status the way wait(2) does, so exit code 1 arrives
    # as 256. os.waitstatus_to_exitcode turns that back into 1.
    return os.waitstatus_to_exitcode(os.system(f"{command} > /dev/null 2>&1"))


def test_exit_code_reflects_differences():
    file_a = data_for_tests_dir / "test_a.nc"
    file_b = data_for_tests_dir / "test_b.nc"

    # Default behavior: always exit 0 on a successful run, even when files differ.
    assert _exit_status(f'ncompare "{file_a}" "{file_b}"') == 0

    # With --exit-code: 1 when differences are found, 0 when there are none.
    assert _exit_status(f'ncompare "{file_a}" "{file_b}" --exit-code') == 1
    assert _exit_status(f'ncompare "{file_a}" "{file_a}" --exit-code') == 0


def test_exit_code_2_when_comparison_fails():
    """A failed comparison is 2, so it stays distinguishable from 'files differ'."""
    missing = data_for_tests_dir / "does_not_exist.nc"
    real = data_for_tests_dir / "test_a.nc"

    # Independent of --exit-code: failure is always 2, never 1.
    assert _exit_status(f'ncompare "{missing}" "{real}"') == 2
    assert _exit_status(f'ncompare "{missing}" "{real}" --exit-code') == 2

    # argparse reports an invalid invocation with the same code.
    assert _exit_status("ncompare --not-a-real-flag") == 2


def test_failure_diagnostics_go_to_stderr():
    """Keep stdout parseable: the traceback belongs on stderr, not mixed into the report."""
    missing = data_for_tests_dir / "does_not_exist.nc"
    real = data_for_tests_dir / "test_a.nc"

    result = subprocess.run(
        ["ncompare", str(missing), str(real)], capture_output=True, text=True, check=False
    )

    assert result.returncode == 2
    assert "Traceback" in result.stderr
    assert "Traceback" not in result.stdout
