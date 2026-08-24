import h5py
import netCDF4
import numpy as np

from ncompare.getters import get_root_dims
from ncompare.utility_types import FileToCompare


def test_get_root_dims_pure_hdf5_without_dimension_scales(tmp_path):
    """A pure HDF5 file with no dimension scales reports no root dimensions (no crash)."""
    path = tmp_path / "pure.h5"
    with h5py.File(path, "w") as f:
        f.create_dataset("data", data=np.arange(4))

    assert get_root_dims(FileToCompare(path=path, type="hdf5")) == []


def test_get_root_dims_hdf5_with_dimension_scale(tmp_path):
    """Root dimensions are recovered from HDF5 dimension scales when present.

    Authored with netCDF4 (a coordinate variable is stored as an HDF5 dimension
    scale) so the scale is created portably; the file is then read via the h5py
    path in get_root_dims.
    """
    path = tmp_path / "scaled.h5"
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("x", 5)
        coordinate = ds.createVariable("x", "f4", ("x",))
        coordinate[:] = range(5)

    assert ("x", 5) in get_root_dims(FileToCompare(path=path, type="hdf5"))


# def test_var_properties(ds_3dims_3vars_4coords_1group):
#     with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
#         result = get_var_properties(ds.groups["Group1"], varname="step", file_type="netcdf")
#         assert result.varname == "step"
#         assert result.dtype == "float32"
#         assert result.shape == "(3,)"
#         assert result.chunking == "contiguous"
#         assert result.attributes == {"add_offset": 5, "scale_factor": 0.5}
#
#
# def test_get_scale_factor(ds_3dims_3vars_4coords_1group):
#     with nc.Dataset(ds_3dims_3vars_4coords_1group) as ds:
#         step_varProps = get_var_properties(ds.groups["Group1"], varname="step", file_type="netcdf")
#
#         result = get_and_check_variable_scale_factor(step_varProps, step_varProps)
#         assert result == ("0.5", "0.5")
