from datetime import datetime, timezone

from fastapi import HTTPException, status


def get_current_utc_time():
    try:
        return datetime.now(timezone.utc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting current UTC time: {str(e)}"
        )
