from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List

from fastapi import HTTPException, status
from bson.objectid import ObjectId


def get_current_utc_time():
    try:
        return datetime.now(timezone.utc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting current UTC time: {str(e)}"
        )


def validate_object_id(id: str, error_msg: Optional[str] = "") -> ObjectId:
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


def serialize_data(data: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
    if not data:
        return data

    if isinstance(data, list):
        return [serialize_data(item) if isinstance(item, (dict, list)) else item for item in data]

    serialize_doc = {}
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
