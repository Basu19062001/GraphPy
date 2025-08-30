from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse

from app.core.db import collection
from app.schemas.responses import APIResponseModel
from app.schemas.auth import UserSignupModel, UserSigninModel
from app.logger import logger
from app.utils.auth_utils import auth_services

router = APIRouter()

users_collection = collection("users")


@router.post("/signup", response_model=APIResponseModel, summary="User signup API")
async def signup(user_payload: UserSignupModel = Body(..., description="User signup payload")):
    try:
        user_data = user_payload.to_db()
        email = user_data.get("email")

        existing_user = await users_collection.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

        inserted_result = await users_collection.insert_one(user_data)
        if not inserted_result.acknowledged:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

        logger.info(f"User created with ID: {inserted_result.inserted_id}")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "User created successfully",
                "status": True,
                "data": {"user_id": str(inserted_result.inserted_id)},
            },
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error during signup: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload. Error: {str(e)}")


@router.post("/signin", response_model=APIResponseModel, summary="User signin API")
async def signin(signin_payload: UserSigninModel = Body(..., description="User signin payload")):
    try:
        signin_data = signin_payload.model_dump()
        email = signin_data.get("email")
        password = signin_data.get("password")

        existing_user = await users_collection.find_one({"email": email})
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist")

        hashed_password = existing_user.get("hashed_password")
        if not hashed_password or not auth_services.verify_password(password, hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        access_token = auth_services.create_access_token(data={"sub": str(existing_user.get("_id")), "email": email})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "User signed in successfully",
                "status": True,
                "data": {"access_token": access_token, "token_type": "bearer"},
            },
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error during signin: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during signin: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload. Error: {str(e)}")
