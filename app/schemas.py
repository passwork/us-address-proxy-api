from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int
    data: dict | None = None
    msg: str


class LoginRequest(BaseModel):
    account: str = Field(..., min_length=1, max_length=64)
    pwd: str = Field(..., min_length=1, max_length=128)


class LoginData(BaseModel):
    token: str
    expires_in: int


class LoginResponse(BaseResponse):
    data: LoginData


class AddressData(BaseModel):
    address: dict


class AddressResponse(BaseResponse):
    data: AddressData
