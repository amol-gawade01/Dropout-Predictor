from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import UUID

import jwt

from jwt.exceptions import (
    InvalidTokenError,
)

from pwdlib import PasswordHash

from sqlalchemy.orm import Session

from backend.app.core.config import (
    get_settings,
)

from backend.app.db.models import (
    Student,
    UserAccount,
)


password_hasher = (
    PasswordHash.recommended()
)


# ============================================================
# PASSWORD
# ============================================================


def hash_password(
    password: str,
) -> str:

    return password_hasher.hash(
        password
    )


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:

    return password_hasher.verify(
        plain_password,
        password_hash,
    )


# ============================================================
# JWT
# ============================================================


def create_access_token(
    user: UserAccount,
) -> tuple[str, int]:

    settings = get_settings()

    expire_minutes = (
        settings
        .access_token_expire_minutes
    )

    now = datetime.now(
        timezone.utc
    )

    payload = {

        "sub":
            str(
                user.user_id
            ),

        "role":
            user.role,

        "iat":
            now,

        "exp":
            now
            + timedelta(
                minutes=
                    expire_minutes
            ),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=
            settings.jwt_algorithm,
    )

    return (
        token,
        expire_minutes * 60,
    )


def decode_access_token(
    token: str,
) -> dict:

    settings = get_settings()

    try:

        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm
            ],
        )

    except InvalidTokenError as exc:

        raise ValueError(
            "Invalid or expired token"
        ) from exc


# ============================================================
# AUTHENTICATE
# ============================================================


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):

    user = (
        db.query(UserAccount)
        .filter(
            UserAccount.email
            == email.lower().strip()
        )
        .first()
    )

    if user is None:

        return None

    if not user.is_active:

        return None

    if not verify_password(
        password,
        user.password_hash,
    ):

        return None

    return user


# ============================================================
# CREATE ACCOUNT
# ============================================================


def create_user_account(
    db: Session,
    email: str,
    password: str,
    display_name: str,
    role: str,
    student_code: str | None = None,
):

    email = (
        email
        .lower()
        .strip()
    )

    existing = (
        db.query(UserAccount)
        .filter(
            UserAccount.email
            == email
        )
        .first()
    )

    if existing:

        raise ValueError(
            "Email already registered"
        )


    role = role.upper()

    if role not in {
        "STUDENT",
        "FACULTY",
        "ADMIN",
    }:

        raise ValueError(
            "Invalid role"
        )


    student_id = None


    # ========================================================
    # STUDENT ACCOUNT
    # ========================================================

    if role == "STUDENT":

        if not student_code:

            raise ValueError(
                "student_code is required "
                "for STUDENT accounts"
            )

        student = (
            db.query(Student)
            .filter(
                Student.student_code
                == student_code
            )
            .first()
        )

        if student is None:

            raise ValueError(
                "Student not found"
            )

        existing_student_account = (
            db.query(UserAccount)
            .filter(
                UserAccount.student_id
                == student.student_id
            )
            .first()
        )

        if existing_student_account:

            raise ValueError(
                "This student already "
                "has an account"
            )

        student_id = (
            student.student_id
        )


    # ========================================================
    # NON-STUDENT ACCOUNT
    # ========================================================

    elif student_code is not None:

        raise ValueError(
            "student_code can only be "
            "used for STUDENT accounts"
        )


    user = UserAccount(

        email=
            email,

        password_hash=
            hash_password(
                password
            ),

        role=
            role,

        display_name=
            display_name,

        student_id=
            student_id,

        is_active=
            True,
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user