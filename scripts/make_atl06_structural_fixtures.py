# Copyright 2024 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software calls the following third-party software,
# which is subject to the terms and conditions of its licensor, as applicable.
# Users must license their own copies; the links are provided for convenience only.
#
# h5py - BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause
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

"""Build structure-only ATL06 test fixtures from real granules.

``ncompare`` compares metadata only -- dtype, shape, chunking, attributes, scale
factor, dimensions, and group structure -- and never reads data values. So the
integration fixtures only need to reproduce a granule's *structure*, not its
science data.

An HDF5 dataset whose chunks are never written occupies essentially no space, so
a clone that declares the same shape, dtype, chunking, and attributes -- but
writes nothing -- is a faithful structural stand-in at a tiny fraction of the
size (~32 MB of granules becomes ~128 KB of gzipped fixtures). That makes the
comparison test hermetic: no network, no Earthdata credentials, and a difference
count that cannot drift when NASA reprocesses the collection.

Run this only when the fixtures need regenerating (for example, to track a new
ATL06 version). It needs the real granules, which do require credentials::

    uv run python scripts/make_atl06_structural_fixtures.py \
        ~/.cache/icesat2_test_data/ATL06_20230816161508_08782002_007_01.h5 \
        ~/.cache/icesat2_test_data/ATL06_20230816234629_08822013_007_01.h5

After regenerating, re-run the comparison test and update the expected
difference count if the new structure legitimately changes it.
"""

import argparse
import gzip
import shutil
import sys
import tempfile
from pathlib import Path

import h5py

# Attributes that encode HDF5 dimension-scale bookkeeping. These hold object
# references (or the labels tied to them), so they are rebuilt through the
# dimension-scale API rather than copied verbatim -- a raw copy would embed
# object tokens that are meaningless in the new file.
DIMENSION_SCALE_ATTRIBUTES = frozenset({"CLASS", "NAME", "DIMENSION_LIST", "REFERENCE_LIST"})

# Where the fixtures live, relative to the repository root.
FIXTURE_DIR = Path(__file__).parent.parent / "tests" / "data" / "atl06_structure"


def _copy_attributes(source: h5py.HLObject, destination: h5py.HLObject) -> None:
    """Copy attributes, leaving dimension-scale bookkeeping to be rebuilt."""
    for key, value in source.attrs.items():
        if key in DIMENSION_SCALE_ATTRIBUTES:
            continue
        try:
            destination.attrs.create(key, value)
        except (TypeError, ValueError, OSError) as err:
            print(f"  ! attribute {key!r} on {source.name}: {err}", file=sys.stderr)


def _shell_kwargs(dataset: h5py.Dataset) -> dict:
    """Build ``create_dataset`` arguments that mirror a dataset's structure."""
    kwargs: dict = {"shape": dataset.shape, "dtype": dataset.dtype}

    if dataset.chunks is not None:
        kwargs["chunks"] = dataset.chunks
        # ATL06 declares chunk shapes larger than the data shape in places.
        # HDF5 only permits that on a resizable dataset, so mark every
        # dimension unlimited in order to preserve chunking exactly.
        kwargs["maxshape"] = (None,) * len(dataset.shape)

    if dataset.compression is not None:
        kwargs["compression"] = dataset.compression
        if dataset.compression_opts is not None:
            kwargs["compression_opts"] = dataset.compression_opts

    try:
        if dataset.fillvalue is not None:
            kwargs["fillvalue"] = dataset.fillvalue
    except (TypeError, ValueError):
        pass

    return kwargs


def write_structural_clone(source_path: Path, destination_path: Path) -> None:
    """Write a structure-only copy of an HDF5 file, containing no data values."""
    # (dataset path, dimension index, scale path), collected while walking and
    # applied afterwards, once every dataset exists to be attached.
    pending_scales: list[tuple[str, int, str]] = []

    with h5py.File(source_path, "r") as source, h5py.File(destination_path, "w") as destination:
        _copy_attributes(source, destination)

        def visit(name: str, obj: h5py.HLObject) -> None:
            if isinstance(obj, h5py.Group):
                _copy_attributes(obj, destination.require_group(name))
                return
            if not isinstance(obj, h5py.Dataset):
                return

            try:
                new_dataset = destination.create_dataset(name, **_shell_kwargs(obj))
            except (TypeError, ValueError, OSError):
                # Long variable-length strings can overflow the object header
                # once a dataset is resizable. Fall back to a plain contiguous
                # shell, which still carries the right shape and dtype.
                try:
                    new_dataset = destination.create_dataset(name, shape=obj.shape, dtype=obj.dtype)
                except (TypeError, ValueError, OSError) as err:
                    print(f"  ! dataset {name}: {err}", file=sys.stderr)
                    return

            _copy_attributes(obj, new_dataset)

            if obj.attrs.get("CLASS", b"") == b"DIMENSION_SCALE":
                label = obj.attrs.get("NAME", b"")
                new_dataset.make_scale(label.decode() if isinstance(label, bytes) else str(label))
            else:
                for index, dimension in enumerate(obj.dims):
                    # Record each scale's full path. ``dimension.keys()`` yields
                    # the NAME attribute, which is not resolvable for scales
                    # that live in subgroups.
                    for scale in dimension.values():
                        pending_scales.append((name, index, scale.name))

        source.visititems(visit)

        attached = 0
        for dataset_path, index, scale_path in pending_scales:
            try:
                destination[dataset_path].dims[index].attach_scale(destination[scale_path])
                attached += 1
            except (KeyError, RuntimeError, OSError) as err:
                print(f"  ! scale {scale_path} -> {dataset_path}[{index}]: {err}", file=sys.stderr)

        if attached != len(pending_scales):
            raise RuntimeError(
                f"attached only {attached} of {len(pending_scales)} dimension scales; "
                "the fixture would not faithfully represent the source structure"
            )
        print(f"  attached {attached} dimension scales")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("granule_1", type=Path, help="path to the first real ATL06 granule")
    parser.add_argument("granule_2", type=Path, help="path to the second real ATL06 granule")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=FIXTURE_DIR,
        help=f"where to write the fixtures (default: {FIXTURE_DIR})",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for number, granule in enumerate((args.granule_1, args.granule_2), start=1):
        if not granule.exists():
            parser.error(f"granule not found: {granule}")

        fixture = args.output_dir / f"atl06_granule_{number}_structure.h5.gz"
        print(f"{granule.name} -> {fixture.name}")

        # Build uncompressed, then gzip: the fixtures are committed, and gzip
        # takes them from ~1.3 MB to ~128 KB combined.
        with tempfile.TemporaryDirectory() as tmpdir:
            uncompressed = Path(tmpdir) / "structure.h5"
            write_structural_clone(granule, uncompressed)
            with open(uncompressed, "rb") as raw, gzip.open(fixture, "wb", compresslevel=9) as gz:
                shutil.copyfileobj(raw, gz)

        source_mb = granule.stat().st_size / 1024**2
        fixture_kb = fixture.stat().st_size / 1024
        print(f"  {source_mb:.1f} MB -> {fixture_kb:.0f} KB")


if __name__ == "__main__":
    main()
