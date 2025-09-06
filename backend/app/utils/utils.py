from datetime import datetime, timezone

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
