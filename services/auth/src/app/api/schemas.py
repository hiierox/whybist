from pydantic import UUID4, BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str
    password: str = Field(..., min_length=6, max_length=1024)


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str | None = Field(
        None, min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$'
        )
    password: str = Field(..., min_length=6, max_length=1024)


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=1024)
    new_password: str = Field(..., min_length=6, max_length=1024)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class UserResponse(BaseModel):
    id: UUID4
    email: EmailStr
    username: str | None


class RefreshRequest(BaseModel):
    refresh_token: str
