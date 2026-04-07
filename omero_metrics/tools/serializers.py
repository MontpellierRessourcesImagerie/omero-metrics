"""
Serialization utilities for passing data between Django views and Dash apps.
Handles microscopemetrics schema objects, pandas dataframes and NumPy arrays for session_state serialization.
"""

import base64
from dataclasses import fields
from typing import Any, Dict

import numpy as np
import pandas as pd
from microscopemetrics_schema.datamodel import microscopemetrics_schema as mm_schema

# Marker keys for custom types
NUMPY_MARKER = "__numpy_array__"
MM_SCHEMA_MARKER = "__mm_schema_obj__"
DATAFRAME_MARKER = "__dataframe__"


def serialize_numpy(arr: np.ndarray) -> Dict[str, Any]:
    """Serialize NumPy array to a JSON-compatible dictionary using binary encoding."""
    return {
        NUMPY_MARKER: True,
        "dtype": str(arr.dtype),
        "shape": list(arr.shape),
        "data": base64.b64encode(arr.tobytes()).decode("ascii"),
    }


def deserialize_numpy(d: Dict[str, Any]) -> np.ndarray:
    """Deserialize a dictionary back to a NumPy array."""
    data = base64.b64decode(d["data"])
    return np.frombuffer(data, dtype=d["dtype"]).reshape(d["shape"])


def serialize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Serialize pandas DataFrame to a JSON-compatible dictionary."""
    return {
        DATAFRAME_MARKER: True,
        "data": df.to_dict(orient="split"),
    }


def deserialize_dataframe(d: Dict[str, Any]) -> pd.DataFrame:
    """Deserialize a dictionary back to a pandas DataFrame."""
    split_data = d["data"]
    if not split_data["data"] and not split_data["columns"]:
        return pd.DataFrame()
    return pd.DataFrame(**split_data)


def serialize_mm_schema_obj(obj: mm_schema.YAMLRoot) -> Dict[str, Any]:
    """Serialize a dataclass instance to a JSON-compatible dictionary."""
    return {
        MM_SCHEMA_MARKER: obj.class_name,
        "data": obj._as_dict,
    }


def serialize(obj: Any) -> Any:
    """
    Recursively serialize an object for JSON storage in session_state.

    Handles:
    - NumPy arrays (binary encoded)
    - Pandas DataFrames
    - MetricsObject
    - Nested structures (lists, dicts)
    """
    if isinstance(obj, np.ndarray):
        return serialize_numpy(obj)
    elif isinstance(obj, pd.DataFrame):
        return serialize_dataframe(obj)
    elif isinstance(obj, mm_schema.EnumDefinitionImpl):
        return str(obj)
    elif isinstance(obj, mm_schema.YAMLRoot):
        # Serialize microscopemetrics_object but also process its fields recursively
        result = {
            MM_SCHEMA_MARKER: obj.class_name,
            "data": {},
        }
        for field in fields(obj):
            value = getattr(obj, field.name)
            result["data"][field.name] = serialize(value)
        return result
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize(item) for item in obj]
    else:
        return obj


def deserialize(obj: Any) -> Any:
    """
    Recursively deserialize an object from JSON storage.

    Args:
        obj: The object to deserialize
    """
    if isinstance(obj, dict):
        if NUMPY_MARKER in obj:
            return deserialize_numpy(obj)
        elif DATAFRAME_MARKER in obj:
            return deserialize_dataframe(obj)
        elif MM_SCHEMA_MARKER in obj:
            class_name = obj[MM_SCHEMA_MARKER]
            data = {k: deserialize(v) for k, v in obj["data"].items()}

            return getattr(mm_schema, class_name)(**data)

        else:
            return {k: deserialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deserialize(item) for item in obj]
    else:
        return obj


def deserialize_partial(context: dict, *keys: str) -> dict:
    """Deserialize only the specified keys from a context dict.

    This avoids the cost of recursively deserializing the entire context
    (which may contain large numpy arrays and mm_schema objects) when
    a callback only needs a few plain-value keys.
    """
    return {k: deserialize(context[k]) for k in keys if k in context}
