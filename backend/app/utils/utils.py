from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException, status
from bson.objectid import ObjectId


def get_current_utc_time():
    try:
        return datetime.now(timezone.utc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting current UTC time: {str(e)}"
        )


def validate_object_id(id: str, error_msg: str) -> ObjectId:
    try:
        if not ObjectId.is_valid(id):
            raise ValueError("Invalid objectId Format")
        return ObjectId(id)

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error while validating ObjectId: {str(e)}"
        )


def serialize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if not data:
        return data

    serialize_doc = dict()

    for key, value in data.items():
        if isinstance(value, ObjectId):
            serialize_doc[key] = str(value)
        elif isinstance(value, dict):
            serialize_doc[key] = serialize_data(value)
        elif isinstance(value, list):
            serialize_doc[key] = [serialize_data(item) if isinstance(item, dict) else item for item in value]
        else:
            serialize_doc[key] = value

    return serialize_doc
