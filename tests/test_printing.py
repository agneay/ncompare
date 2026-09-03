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


import pytest
from colorama import Fore, Style

from ncompare.printing import Outputter


def test_list_of_strings_diff(outputter_to_console):
    left, right, shared = outputter_to_console.lists_diff(
        ["hey", "yo", "beebop"], ["what", "is", "this", "beebop"]
    )

    assert (left, right, shared) == (2, 3, 1)


def test_column_widths_wrong_length_raises():
    """Passing other than three column widths is rejected with a ValueError (not an assert)."""
    with pytest.raises(ValueError):
        Outputter(column_widths=(10, 20))


def test_add_to_history_records_one_row_with_ansi_and_newlines_stripped():
    """A single call records one row; ANSI codes/newlines are stripped and non-strings coerced."""
    out = Outputter(keep_print_history=True)
    out._add_to_history("\x1b[31mred\x1b[0m", "plain\n", 42)

    assert out._line_history == [["red", "plain", "42"]]


def test_no_color_state_is_restored_after_context_exit():
    """`no_color=True` must not permanently blank colorama's global Fore/Style.

    Regression test: previously the color singletons were blanked and never
    restored, so a no-color comparison left later comparisons (and any other
    in-process colorama users) colorless.
    """
    original_red = Fore.RED
    original_reset = Style.RESET_ALL
    assert original_red != ""  # sanity check: colors are present to begin with

    with Outputter(no_color=True):
        # Colors are stripped while the no-color Outputter is active.
        assert Fore.RED == ""
        assert Style.RESET_ALL == ""

    # ...and restored on exit, so subsequent output can be colorized again.
    assert Fore.RED == original_red
    assert Style.RESET_ALL == original_reset
