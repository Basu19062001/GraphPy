from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponseModel(BaseModel):
    message: str = Field(..., description="A message describing the result of the API call")
    status: bool = Field(..., description="Indicates whether the API call was successful or not")


class APIListResponseModel(BaseModel, Generic[T]):
    message: str = Field(..., description="A message describing the result of the API call")
    status: bool = Field(..., description="Indicates whether the API call was successful or not")
    data: List[T] = Field(..., description="A list of items returned by the API call")
