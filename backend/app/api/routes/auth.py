from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from backend.app.core.auth import (
    get_current_user,
    require_roles,
)

from backend.app.db.models import (
    Student,
    UserAccount,
)

from backend.app.schemas.auth import (
    AccountStatusRequest,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.schemas.auth import (
    CreateUserRequest,
    LoginRequest,
)

from backend.app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user_account,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# LOGIN
# ============================================================


@router.post("/login")
def login(

    payload: LoginRequest,

    db: Session = Depends(
        get_db
    ),
):

    user = authenticate_user(

        db=db,

        email=
            payload.email,

        password=
            payload.password,
    )


    if user is None:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=(
                "Invalid email or password"
            ),
        )


    token, expires_in = (
        create_access_token(
            user
        )
    )


    return {

        "access_token":
            token,

        "token_type":
            "bearer",

        "expires_in":
            expires_in,

        "user": {

            "user_id":
                str(
                    user.user_id
                ),

            "email":
                user.email,

            "display_name":
                user.display_name,

            "role":
                user.role,
        },
    }


# ============================================================
# CURRENT USER
# ============================================================


@router.get("/me")
def me(

    current_user:
        UserAccount
        = Depends(
            get_current_user
        ),

    db: Session = Depends(
        get_db
    ),
):

    student_code = None


    if (
        current_user.student_id
        is not None
    ):

        student = db.get(
            Student,
            current_user.student_id,
        )

        if student:

            student_code = (
                student.student_code
            )


    return {

        "user_id":
            str(
                current_user.user_id
            ),

        "email":
            current_user.email,

        "display_name":
            current_user.display_name,

        "role":
            current_user.role,

        "student_code":
            student_code,

        "is_active":
            current_user.is_active,
    }


# ============================================================
# ADMIN: CREATE USER
# ============================================================


@router.post("/users")
def admin_create_user(

    payload:
        CreateUserRequest,

    current_admin:
        UserAccount
        = Depends(
            require_roles(
                "ADMIN"
            )
        ),

    db: Session = Depends(
        get_db
    ),
):

    try:

        user = (
            create_user_account(

                db=db,

                email=
                    payload.email,

                password=
                    payload.password,

                display_name=
                    payload
                    .display_name,

                role=
                    payload.role,

                student_code=
                    payload
                    .student_code,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    return {

        "message":
            "User created",

        "user": {

            "user_id":
                str(
                    user.user_id
                ),

            "email":
                user.email,

            "display_name":
                user.display_name,

            "role":
                user.role,
        },
    }

@router.patch(
    "/users/{user_id}/status"
)
def change_user_status(

    user_id: UUID,

    payload:
        AccountStatusRequest,

    current_admin:
        UserAccount
        = Depends(
            require_roles(
                "ADMIN"
            )
        ),

    db: Session = Depends(
        get_db
    ),
):

    user = db.get(
        UserAccount,
        user_id,
    )


    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    if (
        user.user_id
        == current_admin.user_id
        and not payload.is_active
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "You cannot deactivate "
                "your own account"
            ),
        )


    user.is_active = (
        payload.is_active
    )

    db.commit()

    db.refresh(user)


    return {

        "user_id":
            str(
                user.user_id
            ),

        "is_active":
            user.is_active,
    }