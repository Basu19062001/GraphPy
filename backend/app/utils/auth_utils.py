import re
from typing import Optional
from datetime import timedelta

from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.utils.utils import get_current_utc_time
from app.core.config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def password_validation(cls, password: str) -> str:
        if " " in password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password should not contain spaces")

        if not re.search(r"[a-z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password should contain at least one lowercase letter"
            )

        if not re.search(r"[A-Z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password should contain at least one uppercase letter"
            )

        if not re.search(r"\d", password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password should contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}/<>|_+=-]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password should contain at least one special character"
            )

        if re.search(r"(.)\1{2,}", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot contain repetitive characters",
            )

        return cls.generate_hashed_password(password)

    @classmethod
    def generate_hashed_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict, access_token_expire_time: Optional[int] = None) -> str:
        try:
            encoded_data = data.copy()

            expire = get_current_utc_time() + timedelta(
                minutes=access_token_expire_time if access_token_expire_time else 30 * 2 * 24 * 7  # 1 weeks
            )

            encoded_data["exp"] = expire
            encoded_data["iat"] = get_current_utc_time()

            encoded_jwt = jwt.encode(encoded_data, settings.JWT_SECRET_KEY, algorithm="HS256")
            return encoded_jwt

        except JWTError as je:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"JWT Error: {str(je)}")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating access token: {str(e)}"
            )

    @classmethod
    def verify_access_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.AUTHENTICATION_ALGORITHM])

            if isinstance(payload, dict) or "sub" not in payload:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

            return payload

        except JWTError as je:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"JWT Error: {str(je)}")

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error verifying access token: {str(e)}")


auth_services = AuthService()
