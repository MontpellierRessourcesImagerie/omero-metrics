"""Tests for omero_metrics.tools.load module."""

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema

from omero_metrics.tools.data_type import (
    DATASET_TYPES,
    INPUT_IMAGES_MAPPING,
    KKM_MAPPINGS,
)


class TestSchemaContract:
    """Verify that the installed microscopemetrics_schema matches what the code expects.

    These tests catch schema version mismatches early — if a class is renamed,
    a field is removed, or key_measurements changes shape, these will fail
    before the error surfaces at runtime in the Docker container.
    """

    @pytest.mark.parametrize("cls_name", DATASET_TYPES)
    def test_dataset_classes_exist(self, cls_name):
        cls = getattr(mm_schema, cls_name, None)
        assert cls is not None, f"{cls_name} not found in schema"
        assert dataclasses.is_dataclass(cls)

    @pytest.mark.parametrize("cls_name", DATASET_TYPES)
    def test_dataset_has_required_fields(self, cls_name):
        """Every dataset class must have the fields the code accesses."""
        cls = getattr(mm_schema, cls_name)
        field_names = {f.name for f in dataclasses.fields(cls)}
        for required in [
            "name",
            "processed",
            "input_parameters",
            "input_data",
            "output",
            "acquisition_datetime",
            "data_reference",
            "microscope",
        ]:
            assert required in field_names, f"{cls_name} missing field '{required}'"

    @pytest.mark.parametrize(
        "cls_name,input_attr",
        list(INPUT_IMAGES_MAPPING.items()),
    )
    def test_input_data_has_image_field(self, cls_name, input_attr):
        """The input data class must have the image list field we expect."""
        input_data_cls_name = cls_name.replace("Dataset", "InputData")
        input_data_cls = getattr(mm_schema, input_data_cls_name, None)
        assert (
            input_data_cls is not None
        ), f"{input_data_cls_name} not found in schema"
        field_names = {f.name for f in dataclasses.fields(input_data_cls)}
        assert (
            input_attr in field_names
        ), f"{input_data_cls_name} missing field '{input_attr}'"

    def test_field_illumination_key_measurement_is_singular(self):
        """The new schema uses FieldIlluminationKeyMeasurement (singular),
        not the old FieldIlluminationKeyMeasurements (plural)."""
        assert hasattr(mm_schema, "FieldIlluminationKeyMeasurement"), (
            "Schema missing FieldIlluminationKeyMeasurement (singular) — "
            "is the old schema installed?"
        )

    def test_field_illumination_output_key_measurements_is_list(self):
        """key_measurements must be typed as a list in the new schema."""
        cls = mm_schema.FieldIlluminationOutput
        for f in dataclasses.fields(cls):
            if f.name == "key_measurements":
                type_str = str(f.type)
                assert (
                    "list" in type_str.lower() or "List" in type_str
                ), f"key_measurements type should contain list, got: {f.type}"
                return
        pytest.fail("FieldIlluminationOutput has no key_measurements field")

    def test_key_measurement_has_channel_name(self):
        """context_loaders.py accesses km.channel_name — field must exist."""
        field_names = {
            f.name
            for f in dataclasses.fields(mm_schema.FieldIlluminationKeyMeasurement)
        }
        assert "channel_name" in field_names

    @pytest.mark.parametrize(
        "ds_type,kkm_fields",
        list(KKM_MAPPINGS.items()),
    )
    def test_kkm_fields_exist_on_key_measurement(self, ds_type, kkm_fields):
        """Every KKM field referenced in data_type.py must exist on the
        corresponding KeyMeasurement class."""
        km_cls_name = ds_type.replace("Dataset", "KeyMeasurement")
        km_cls = getattr(mm_schema, km_cls_name, None)
        assert km_cls is not None, f"{km_cls_name} not found in schema"
        field_names = {f.name for f in dataclasses.fields(km_cls)}
        for kkm in kkm_fields:
            assert kkm in field_names, f"{km_cls_name} missing KKM field '{kkm}'"

    def test_key_measurement_supports_bracket_access(self):
        """context_loaders.py uses km[kkm] — schema objects must support it."""
        km = mm_schema.FieldIlluminationKeyMeasurement(
            channel_name="ch0", max_intensity=42.0
        )
        assert km["channel_name"] == "ch0"
        assert km["max_intensity"] == 42.0

    def test_yaml_roundtrip_field_illumination(self):
        """A FieldIlluminationDataset with key_measurements must survive
        YAML dump/load without errors."""
        from linkml_runtime.dumpers import yaml_dumper
        from linkml_runtime.loaders import yaml_loader

        km = mm_schema.FieldIlluminationKeyMeasurement(
            channel_name="ch0", max_intensity=100.0
        )
        output = mm_schema.FieldIlluminationOutput(
            key_measurements=[km],
            processing_application=["test"],
            processing_version=["1.0"],
            processing_datetime="2024-01-01",
        )
        dataset = mm_schema.FieldIlluminationDataset(
            name="test",
            microscope=mm_schema.Microscope(name="mic"),
            input_parameters=mm_schema.FieldIlluminationInputParameters(),
            input_data=mm_schema.FieldIlluminationInputData(
                field_illumination_images=[
                    mm_schema.Image(
                        name="img",
                        shape_x=64,
                        shape_y=64,
                        shape_z=1,
                        shape_c=1,
                        shape_t=1,
                    )
                ]
            ),
            output=output,
        )
        yaml_str = yaml_dumper.dumps(dataset)
        loaded = yaml_loader.loads(
            yaml_str, target_class=mm_schema.FieldIlluminationDataset
        )
        assert len(loaded.output.key_measurements) == 1
        assert loaded.output.key_measurements[0].channel_name == "ch0"
        assert loaded.output.key_measurements[0].max_intensity == 100.0

    def test_analysis_output_matches_schema(self):
        """Run a real field illumination analysis (same as structure_generator)
        and verify the output conforms to the schema contract."""
        from dataclasses import asdict

        from microscopemetrics.analyses import field_illumination, numpy_to_mm_image
        from microscopemetrics.strategies.field_illumination import (
            _gen_field_illumination_image,
        )

        # Generate synthetic image — mirrors structure_generator.py
        image = numpy_to_mm_image(
            array=_gen_field_illumination_image(
                y_shape=64,
                x_shape=64,
                c_shape=2,
                y_center_rel_offset=[0.1, -0.1],
                x_center_rel_offset=[0.1, -0.1],
                dispersion=[0.8, 0.8],
                target_min_intensity=[0.3, 0.3],
                target_max_intensity=[0.8, 0.8],
                do_noise=False,
                signal=[500, 500],
                dtype=np.uint16,
            ),
            channel_names=["DAPI", "FITC"],
            name="test_image",
        )

        dataset = mm_schema.FieldIlluminationDataset(
            name="test_fi",
            microscope=mm_schema.Microscope(name="TestScope"),
            input_parameters=mm_schema.FieldIlluminationInputParameters(),
            input_data=mm_schema.FieldIlluminationInputData(
                field_illumination_images=[image]
            ),
        )

        # analyse modifies dataset in-place and returns bool
        success = field_illumination.analyse_field_illumination(dataset)
        assert success is True

        # Verify output structure
        assert dataset.processed is True
        assert isinstance(dataset.output, mm_schema.FieldIlluminationOutput)

        # key_measurements must be a list of FieldIlluminationKeyMeasurement
        km_list = dataset.output.key_measurements
        assert isinstance(km_list, list)
        assert len(km_list) == 2  # one per channel
        for km in km_list:
            assert isinstance(km, mm_schema.FieldIlluminationKeyMeasurement)
            assert km.channel_name is not None
            # KKM fields from data_type.py must be populated
            for kkm_field in KKM_MAPPINGS["FieldIlluminationDataset"]:
                assert hasattr(km, kkm_field), f"Missing KKM field: {kkm_field}"
                assert km[kkm_field] is not None, f"KKM field {kkm_field} is None"

        # Must survive asdict (used by get_km_mm_metrics_dataset)
        rows = [asdict(km) for km in km_list]
        assert len(rows) == 2
        assert all("channel_name" in row for row in rows)

        # Must survive YAML roundtrip (used by load_dataset)
        # Clear all array_data before dump — numpy arrays can't be YAML-serialized;
        # the real code stores images separately in OMERO
        def _clear_arrays(obj, visited=None):
            if visited is None:
                visited = set()
            obj_id = id(obj)
            if obj_id in visited:
                return
            visited.add(obj_id)
            if hasattr(obj, "array_data"):
                obj.array_data = None
            if dataclasses.is_dataclass(obj):
                for f in dataclasses.fields(obj):
                    val = getattr(obj, f.name)
                    if isinstance(val, list):
                        for item in val:
                            _clear_arrays(item, visited)
                    elif dataclasses.is_dataclass(val):
                        _clear_arrays(val, visited)

        _clear_arrays(dataset)

        from linkml_runtime.dumpers import yaml_dumper
        from linkml_runtime.loaders import yaml_loader

        yaml_str = yaml_dumper.dumps(dataset)
        loaded = yaml_loader.loads(
            yaml_str, target_class=mm_schema.FieldIlluminationDataset
        )
        assert len(loaded.output.key_measurements) == 2
        assert (
            loaded.output.key_measurements[0].channel_name == km_list[0].channel_name
        )


pytest.importorskip("omero", reason="omero package not available locally")

from omero_metrics.tools.load import (
    get_km_mm_metrics_dataset,
    load_table_mm_metrics,
    modify_column_name,
    roi_finder,
)


class TestModifyColumnName:
    def test_increment_channel_number(self):
        assert modify_column_name("intensity_ch0", 0) == "intensity_ch0"
        assert modify_column_name("intensity_ch0", 3) == "intensity_ch3"
        assert modify_column_name("intensity_ch2", 5) == "intensity_ch7"

    def test_no_channel_pattern(self):
        assert modify_column_name("name", 5) == "name"
        assert modify_column_name("description", 10) == "description"

    def test_channel_in_middle(self):
        assert modify_column_name("max_ch0_intensity", 2) == "max_ch2_intensity"

    def test_zero_offset(self):
        assert modify_column_name("ch0", 0) == "ch0"
        assert modify_column_name("ch5", 0) == "ch5"


class TestRoiFinder:
    def test_rectangle_roi(self):
        rect = MagicMock()
        rect.name = "rect1"
        rect.x = 10
        rect.y = 20
        rect.w = 100
        rect.h = 200
        roi = MagicMock(spec=mm_schema.Roi)
        roi.name = "test_roi"
        roi.rectangles = [rect]
        roi.lines = None
        roi.points = None

        result = roi_finder(roi)
        assert result["type"] == "Rectangle"
        assert len(result["data"]) == 1
        assert result["data"][0]["roi_name"] == "test_roi"
        assert result["data"][0]["x"] == 10
        assert result["data"][0]["w"] == 100

    def test_line_roi(self):
        line = MagicMock()
        line.name = "line1"
        line.x1 = 0
        line.y1 = 0
        line.x2 = 100
        line.y2 = 100
        roi = MagicMock(spec=mm_schema.Roi)
        roi.name = "line_roi"
        roi.rectangles = None
        roi.lines = [line]
        roi.points = None

        result = roi_finder(roi)
        assert result["type"] == "Line"
        assert len(result["data"]) == 1
        assert result["data"][0]["x1"] == 0
        assert result["data"][0]["x2"] == 100

    def test_point_roi(self):
        point = MagicMock()
        point.name = "point1"
        point.x = 50
        point.y = 75
        point.c = 0
        roi = MagicMock(spec=mm_schema.Roi)
        roi.name = "point_roi"
        roi.rectangles = None
        roi.lines = None
        roi.points = [point]

        result = roi_finder(roi)
        assert result["type"] == "Point"
        assert len(result["data"]) == 1
        assert result["data"][0]["x"] == 50
        assert result["data"][0]["c"] == 0

    def test_empty_roi(self):
        roi = MagicMock(spec=mm_schema.Roi)
        roi.rectangles = None
        roi.lines = None
        roi.points = None

        result = roi_finder(roi)
        assert result is None

    def test_multiple_rectangles(self):
        rects = []
        for i in range(3):
            r = MagicMock()
            r.name = f"rect{i}"
            r.x = i * 10
            r.y = i * 20
            r.w = 50
            r.h = 50
            rects.append(r)

        roi = MagicMock(spec=mm_schema.Roi)
        roi.name = "multi_roi"
        roi.rectangles = rects
        roi.lines = None
        roi.points = None

        result = roi_finder(roi)
        assert result["type"] == "Rectangle"
        assert len(result["data"]) == 3


class TestLoadTableMmMetrics:
    def test_single_table(self):
        col1 = MagicMock()
        col1.name = "channel"
        col1.values = ["DAPI", "FITC", "TRITC"]
        col2 = MagicMock()
        col2.name = "intensity"
        col2.values = ["100", "200", "300"]

        table = MagicMock(spec=mm_schema.Table)
        table.columns = [col1, col2]

        result = load_table_mm_metrics(table)
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["channel", "intensity"]
        assert len(result) == 3
        # numeric columns should be converted
        assert result["intensity"].dtype in [np.int64, np.float64]

    def test_list_of_tables(self):
        col1 = MagicMock()
        col1.name = "val_ch0"
        col1.values = ["1.0", "2.0"]
        table1 = MagicMock(spec=mm_schema.Table)
        table1.columns = [col1]

        col2 = MagicMock()
        col2.name = "val_ch0"
        col2.values = ["3.0", "4.0"]
        table2 = MagicMock(spec=mm_schema.Table)
        table2.columns = [col2]

        result = load_table_mm_metrics([table1, table2])
        assert isinstance(result, pd.DataFrame)
        # Second table's ch0 should be renamed to ch1
        assert "val_ch0" in result.columns
        assert "val_ch1" in result.columns

    def test_none_input(self):
        assert load_table_mm_metrics(None) is None

    def test_empty_list(self):
        assert load_table_mm_metrics([]) is None

    def test_table_with_nan_strings(self):
        col = MagicMock()
        col.name = "values"
        col.values = ["1.0", "nan", "3.0"]
        table = MagicMock(spec=mm_schema.Table)
        table.columns = [col]

        result = load_table_mm_metrics(table)
        assert pd.isna(result["values"].iloc[1])

    def test_non_numeric_columns_preserved(self):
        col = MagicMock()
        col.name = "labels"
        col.values = ["alpha", "beta", "gamma"]
        table = MagicMock(spec=mm_schema.Table)
        table.columns = [col]

        result = load_table_mm_metrics(table)
        assert result["labels"].dtype == object
        assert list(result["labels"]) == ["alpha", "beta", "gamma"]


class TestGetKmMmMetricsDataset:
    def test_basic_key_measurements(self):
        km1 = MagicMock()
        km1.__dataclass_fields__ = {}

        # Use a real dataclass-like approach
        @dataclass
        class FakeKM:
            name: str = ""
            max_intensity: float = 0.0
            center_fraction: float = 0.0

        dataset = MagicMock()
        dataset.output.key_measurements = [
            FakeKM(name="ch0", max_intensity=255.0, center_fraction=0.85),
            FakeKM(name="ch1", max_intensity=200.0, center_fraction=0.75),
        ]

        result = get_km_mm_metrics_dataset(dataset)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "max_intensity" in result.columns
        assert result["max_intensity"].dtype in [np.float64, np.int64]

    def test_nan_replacement(self):
        @dataclass
        class FakeKM:
            value: str = "nan"

        dataset = MagicMock()
        dataset.output.key_measurements = [FakeKM(value="nan")]

        result = get_km_mm_metrics_dataset(dataset)
        assert pd.isna(result["value"].iloc[0])
