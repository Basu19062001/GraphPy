import re

from fastapi import HTTPException, status
from passlib.context import CryptContext


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


auth_services = AuthService()
