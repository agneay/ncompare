import h5py
import netCDF4 as nC

from ncompare.getters import get_root_attributes
from ncompare.utility_types import FileToCompare


def test_get_root_attributes_netcdf(tmp_path):
    filepath = tmp_path / "test_root_attrs.nc"
    with nC.Dataset(filepath, mode="w") as ds:
        ds.setncattr("title", "Test Dataset")
        ds.setncattr("version", "1.0")

    result = get_root_attributes(FileToCompare(filepath, type="netcdf"))

    assert result == {"title": "Test Dataset", "version": "1.0"}


def test_get_root_attributes_hdf5(tmp_path):
    filepath = tmp_path / "test_root_attrs.h5"
    with h5py.File(filepath, mode="w") as ds:
        ds.attrs["title"] = "Test Dataset"
        ds.attrs["version"] = "1.0"

    result = get_root_attributes(FileToCompare(filepath, type="hdf5"))

    assert result == {"title": "Test Dataset", "version": "1.0"}


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
