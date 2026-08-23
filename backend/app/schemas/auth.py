from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


RoleType = Literal[
    "STUDENT",
    "FACULTY",
    "ADMIN",
]


# ============================================================
# LOGIN
# ============================================================


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


# ============================================================
# TOKEN
# ============================================================


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_in: int


# ============================================================
# ADMIN CREATE USER
# ============================================================


class CreateUserRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    display_name: str = Field(
        min_length=1,
        max_length=128,
    )

    role: RoleType

    # Required only when role=STUDENT.
    student_code: str | None = None


# ============================================================
# USER RESPONSE
# ============================================================


class UserResponse(BaseModel):

    user_id: str

    email: str

    display_name: str

    role: str

    student_code: str | None

    is_active: bool

class AccountStatusRequest(
    BaseModel
):

    is_active: bool