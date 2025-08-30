from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, Field, model_validator, PrivateAttr

from app.utils.auth_utils import auth_services


class UserSignupModel(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    phone_number: str = Field(..., description="Phone number of the user")
    secondary_phone_number: Optional[str] = Field(None, description="Secondary phone number of the user")
    address: str = Field(..., description="Address of the user")
    password: str = Field(..., description="Password for the user account", min_length=8)
    confirm_password: str = Field(..., description="Confirm password", min_length=8)
    _hashed_password: str | None = PrivateAttr()

    @model_validator(mode="after")
    def validate_and_hash_passwords(self):
        if self.password != self.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details=f"Password do not match")
        self._hashed_password = auth_services.password_validation(self.password)
        return self

    def to_db(self) -> dict:
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "secondary_phone_number": self.secondary_phone_number,
            "address": self.address,
            "hashed_password": self._hashed_password,
        }
