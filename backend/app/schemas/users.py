from pydantic import BaseModel, EmailStr, Field


class UserCreateModel(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password for the user account", min_length=8)
    confirm_password: str = Field(..., description="Confirm password", min_length=8)
