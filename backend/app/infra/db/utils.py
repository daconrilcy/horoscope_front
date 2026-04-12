from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Type

from sqlalchemy import DateTime, UUID, inspect


def serialize_orm(obj: Any) -> Dict[str, Any]:
    """
    Robustly serializes an SQLAlchemy ORM object to a dictionary.
    Converts UUIDs and DateTimes to strings.
    """
    data = {}
    try:
        mapper = inspect(obj).mapper
        for column in mapper.column_attrs:
            value = getattr(obj, column.key)
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            data[column.key] = value
    except Exception:
        # Fallback for non-ORM or error
        pass
    return data


def reconstruct_orm(model_class: Type[Any], data: Dict[str, Any]) -> Any:
    """
    Robustly reconstructs an SQLAlchemy ORM object from a dictionary.
    Handles automatic conversion of strings back to UUIDs and DateTimes.
    """
    clean_data = {}
    try:
        mapper = inspect(model_class)
        for key, value in data.items():
            if key not in mapper.all_orm_descriptors:
                continue

            # Type detection from SQLAlchemy Mapper using python_type for robustness
            column = mapper.columns.get(key)
            if column is not None and value is not None and hasattr(column.type, "python_type"):
                py_type = column.type.python_type
                if py_type == uuid.UUID and isinstance(value, str):
                    try:
                        value = uuid.UUID(value)
                    except (ValueError, TypeError):
                        pass
                elif py_type == datetime and isinstance(value, str):
                    try:
                        value = datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        pass

            clean_data[key] = value
    except Exception:
        # Best effort
        clean_data = data

    return model_class(**clean_data)
