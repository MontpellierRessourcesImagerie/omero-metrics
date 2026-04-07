"""Tests for omero_metrics.tools.serializers module."""

import numpy as np
import pandas as pd
import pytest
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema

from omero_metrics.tools.serializers import (
    DATAFRAME_MARKER,
    MM_SCHEMA_MARKER,
    NUMPY_MARKER,
    deserialize,
    deserialize_dataframe,
    deserialize_numpy,
    serialize,
    serialize_dataframe,
    serialize_mm_schema_obj,
    serialize_numpy,
)


class TestSerializeNumpy:
    def test_roundtrip_float64(self, sample_numpy_array):
        serialized = serialize_numpy(sample_numpy_array)
        result = deserialize_numpy(serialized)
        np.testing.assert_array_equal(result, sample_numpy_array)
        assert result.dtype == sample_numpy_array.dtype

    def test_roundtrip_int32(self):
        arr = np.array([1, 2, 3], dtype=np.int32)
        serialized = serialize_numpy(arr)
        result = deserialize_numpy(serialized)
        np.testing.assert_array_equal(result, arr)
        assert result.dtype == np.int32

    def test_roundtrip_3d_array(self):
        arr = np.random.rand(2, 3, 4)
        serialized = serialize_numpy(arr)
        result = deserialize_numpy(serialized)
        np.testing.assert_array_almost_equal(result, arr)
        assert result.shape == (2, 3, 4)

    def test_serialized_format(self, sample_numpy_array):
        serialized = serialize_numpy(sample_numpy_array)
        assert serialized[NUMPY_MARKER] is True
        assert serialized["dtype"] == "float64"
        assert serialized["shape"] == [2, 2]
        assert isinstance(serialized["data"], str)  # base64 string

    def test_empty_array(self):
        arr = np.array([])
        serialized = serialize_numpy(arr)
        result = deserialize_numpy(serialized)
        np.testing.assert_array_equal(result, arr)


class TestSerializeDataframe:
    def test_roundtrip(self, sample_dataframe):
        serialized = serialize_dataframe(sample_dataframe)
        result = deserialize_dataframe(serialized)
        pd.testing.assert_frame_equal(result, sample_dataframe)

    def test_serialized_format(self, sample_dataframe):
        serialized = serialize_dataframe(sample_dataframe)
        assert serialized[DATAFRAME_MARKER] is True
        assert "data" in serialized
        assert "columns" in serialized["data"]
        assert "index" in serialized["data"]

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        serialized = serialize_dataframe(df)
        result = deserialize_dataframe(serialized)
        pd.testing.assert_frame_equal(result, df)

    def test_numeric_dataframe(self):
        df = pd.DataFrame({"a": [1.1, 2.2], "b": [3, 4]})
        serialized = serialize_dataframe(df)
        result = deserialize_dataframe(serialized)
        pd.testing.assert_frame_equal(result, df)


class TestSerializeMmSchemaObj:
    def test_serialize_image(self):
        img = mm_schema.Image(name="test_image", shape_x=512, shape_y=512)
        serialized = serialize_mm_schema_obj(img)
        assert serialized[MM_SCHEMA_MARKER] == "Image"
        assert "data" in serialized


class TestSerializeRecursive:
    def test_serialize_dict_with_numpy(self, sample_numpy_array):
        data = {"key": "value", "array": sample_numpy_array}
        serialized = serialize(data)
        assert serialized["key"] == "value"
        assert serialized["array"][NUMPY_MARKER] is True

    def test_serialize_dict_with_dataframe(self, sample_dataframe):
        data = {"name": "test", "df": sample_dataframe}
        serialized = serialize(data)
        assert serialized["name"] == "test"
        assert serialized["df"][DATAFRAME_MARKER] is True

    def test_serialize_nested_list(self):
        data = [np.array([1, 2]), "text", 42]
        serialized = serialize(data)
        assert serialized[0][NUMPY_MARKER] is True
        assert serialized[1] == "text"
        assert serialized[2] == 42

    def test_serialize_plain_types(self):
        assert serialize("hello") == "hello"
        assert serialize(42) == 42
        assert serialize(3.14) == 3.14
        assert serialize(None) is None
        assert serialize(True) is True

    def test_serialize_nested_dict(self):
        data = {"outer": {"inner": np.array([1, 2, 3])}}
        serialized = serialize(data)
        assert serialized["outer"]["inner"][NUMPY_MARKER] is True


class TestDeserializeRecursive:
    def test_deserialize_numpy(self, sample_numpy_array):
        serialized = serialize(sample_numpy_array)
        result = deserialize(serialized)
        np.testing.assert_array_equal(result, sample_numpy_array)

    def test_deserialize_dataframe(self, sample_dataframe):
        serialized = serialize(sample_dataframe)
        result = deserialize(serialized)
        pd.testing.assert_frame_equal(result, sample_dataframe)

    def test_deserialize_nested(self, sample_numpy_array, sample_dataframe):
        data = {"arr": sample_numpy_array, "df": sample_dataframe, "val": 42}
        serialized = serialize(data)
        result = deserialize(serialized)
        np.testing.assert_array_equal(result["arr"], sample_numpy_array)
        pd.testing.assert_frame_equal(result["df"], sample_dataframe)
        assert result["val"] == 42

    def test_deserialize_plain_dict(self):
        data = {"key": "value", "num": 123}
        result = deserialize(data)
        assert result == data

    def test_deserialize_list(self):
        data = [1, "two", {"three": 3}]
        result = deserialize(data)
        assert result == data

    def test_deserialize_plain_types(self):
        assert deserialize("hello") == "hello"
        assert deserialize(42) == 42
        assert deserialize(None) is None


class TestSerializeDeserializeRoundtrip:
    def test_complex_nested_structure(self, sample_numpy_array, sample_dataframe):
        data = {
            "metadata": {"name": "test", "version": 1},
            "arrays": [sample_numpy_array, sample_numpy_array * 2],
            "table": sample_dataframe,
            "config": {"threshold": 0.5, "enabled": True},
        }
        serialized = serialize(data)
        result = deserialize(serialized)

        assert result["metadata"] == data["metadata"]
        np.testing.assert_array_equal(result["arrays"][0], sample_numpy_array)
        np.testing.assert_array_equal(result["arrays"][1], sample_numpy_array * 2)
        pd.testing.assert_frame_equal(result["table"], sample_dataframe)
        assert result["config"] == data["config"]
