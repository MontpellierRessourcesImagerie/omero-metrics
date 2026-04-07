"""Shared fixtures for unit tests."""

from dataclasses import dataclass, field
from datetime import datetime
from unittest.mock import MagicMock, PropertyMock

import numpy as np
import pandas as pd
import pytest
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema

# --- Mock OMERO objects ---


class MockOwner:
    def getName(self):
        return "test_user"


class MockFile:
    def __init__(self, name="test_file.yaml", file_id=100):
        self._name = name
        self._id = file_id

    def getName(self):
        return self._name

    def getId(self):
        return self._id


class MockAnnotation:
    """Base mock for OMERO annotations."""

    def __init__(
        self,
        ann_id=1,
        ns="microscopemetrics_schema:core",
        description="desc",
        date=None,
    ):
        self._id = ann_id
        self._ns = ns
        self._description = description
        self._date = date or datetime(2024, 1, 15)
        self._owner = MockOwner()

    def getId(self):
        return self._id

    def getNs(self):
        return self._ns

    def getDescription(self):
        return self._description

    def getDate(self):
        return self._date

    def getOwner(self):
        return self._owner


class MockFileAnnotation(MockAnnotation):
    """Mock for OMERO FileAnnotationWrapper."""

    def __init__(
        self, name="test.yaml", file_id=100, content=b"test: data", **kwargs
    ):
        super().__init__(**kwargs)
        self._file = MockFile(name, file_id)
        self._content = content

    def getFile(self):
        return self._file

    def getFileName(self):
        return self._file.getName()

    def getFileInChunks(self):
        return iter([self._content])


class MockMapAnnotation(MockAnnotation):
    """Mock for OMERO MapAnnotationWrapper."""

    def __init__(self, name="test_map", value=None, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._value = value or [("key1", "val1")]

    def getName(self):
        return self._name

    def getValue(self):
        return self._value


class MockGroup:
    def __init__(self, name="TestGroup", description="Test group description"):
        self._name = name
        self._description = description

    def getName(self):
        return self._name

    def getDescription(self):
        return self._description


class MockConnection:
    """Mock for OMERO BlitzGateway."""

    def __init__(self):
        self._objects = {}

    def getObjects(self, obj_type, opts=None):
        return self._objects.get(obj_type, [])

    def getObject(self, obj_type, obj_id=None):
        objects = self._objects.get(obj_type, [])
        for obj in objects:
            if hasattr(obj, "getId") and obj.getId() == obj_id:
                return obj
        if objects:
            return objects[0]
        return MagicMock()

    def getEventContext(self):
        ctx = MagicMock()
        ctx.groupId = 1
        return ctx

    def getUser(self):
        user = MagicMock()
        user.getName.return_value = "test_user"
        user.firstName = "Test"
        user.lastName = "User"
        user.id = 1
        return user

    def deleteObjects(self, **kwargs):
        pass


@pytest.fixture
def mock_conn():
    return MockConnection()


@pytest.fixture
def sample_file_ann_df():
    """Sample file annotations DataFrame."""
    return pd.DataFrame(
        {
            "Name": ["file1.yaml", "file2.yaml"],
            "ID": [1, 2],
            "File_ID": [101, 102],
            "Description": ["desc1", "desc2"],
            "Date": pd.to_datetime(["2024-01-15", "2024-02-20"]),
            "Owner": ["user1", "user2"],
            "NS": [
                "microscopemetrics_schema:analyses/field_illumination",
                "microscopemetrics_schema:core/Table",
            ],
        }
    )


@pytest.fixture
def sample_map_ann_df():
    """Sample map annotations DataFrame."""
    return pd.DataFrame(
        {
            "Name": ["map1", "map2"],
            "ID": [10, 20],
            "Description": ["desc1", "desc2"],
            "Date": pd.to_datetime(["2024-03-10", "2024-04-15"]),
            "Owner": ["user1", "user2"],
            "NS": [
                "microscopemetrics_schema:analyses/field_illumination",
                "microscopemetrics_schema:analyses/psf_beads",
            ],
        }
    )


@pytest.fixture
def sample_numpy_array():
    """Sample NumPy array for serialization tests."""
    return np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64)


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for serialization tests."""
    return pd.DataFrame({"col_a": [1, 2, 3], "col_b": ["x", "y", "z"]})
