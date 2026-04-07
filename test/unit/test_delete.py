"""Tests for omero_metrics.tools.delete module."""

from unittest.mock import MagicMock, patch

import pytest
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema

pytest.importorskip("omero", reason="omero package not available locally")

from omero_metrics.tools.delete import (
    _empty_data_reference,
    delete_data_references,
)


class TestEmptyDataReference:
    def test_clears_all_fields(self):
        ref = mm_schema.DataReference(
            data_uri="http://example.com",
            omero_host="localhost",
            omero_port=4064,
            omero_object_type=mm_schema.OMEROObjectTypeEnum("IMAGE"),
            omero_object_id=42,
        )
        _empty_data_reference(ref)

        assert ref.data_uri is None
        assert ref.omero_host is None
        assert ref.omero_port is None
        assert ref.omero_object_type is None
        assert ref.omero_object_id is None

    def test_already_empty_reference(self):
        ref = mm_schema.DataReference()
        _empty_data_reference(ref)
        assert ref.data_uri is None
        assert ref.omero_object_id is None


class TestDeleteDataReferences:
    def test_delete_data_reference_object(self):
        ref = mm_schema.DataReference(
            omero_host="localhost",
            omero_object_id=1,
        )
        delete_data_references(ref)
        assert ref.omero_host is None
        assert ref.omero_object_id is None

    def test_delete_metrics_object(self):
        img = mm_schema.Image(
            name="test",
            shape_x=512,
            shape_y=512,
            data_reference=mm_schema.DataReference(
                omero_host="localhost",
                omero_object_id=42,
            ),
        )
        delete_data_references(img)
        assert img.data_reference.omero_object_id is None
        assert img.data_reference.omero_host is None

    def test_delete_list_of_objects(self):
        images = [
            mm_schema.Image(
                name=f"img{i}",
                shape_x=512,
                shape_y=512,
                data_reference=mm_schema.DataReference(omero_object_id=i),
            )
            for i in range(3)
        ]
        delete_data_references(images)
        for img in images:
            assert img.data_reference.omero_object_id is None

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError, match="should be a metrics object"):
            delete_data_references("not_a_metrics_object")

    def test_invalid_number_raises(self):
        with pytest.raises(ValueError):
            delete_data_references(42)
