from pydantic import BaseModel, EmailStr, UUID4


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str | None = None
    password: str


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    username: str | None
