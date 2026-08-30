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

"""Shared type definitions used across ncompare."""

from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

valid_file_type_ids = Literal["netcdf", "hdf5"]


@dataclass
class FileToCompare:
    """Represents an input file to compare against, and its file type."""

    path: Path | str
    type: valid_file_type_ids = "netcdf"

    def __post_init__(self):
        # We'll validate the inputs here.
        if not isinstance(self.path, (str, Path)):
            raise TypeError(f"'path' must be a str or Path, was {type(self.path)}")
        if self.type not in ("netcdf", "hdf5"):
            raise ValueError("'type' must be either 'netcdf' or 'hdf5'")


class SummaryDifferencesDict(TypedDict):
    """Represents the number and type of differences between two files."""

    shared: int
    left: int
    right: int
    both: int
    difference_types: set


SummaryDifferenceKeys = Literal["shared", "left", "right", "both"]

VarProperties = namedtuple(
    "VarProperties", "varname, variable, dtype, dimensions, shape, chunking, attributes"
)

GroupPair = namedtuple(
    "GroupPair",
    "group_a_name group_a group_b_name group_b",
    defaults=("", None, "", None),
)
