from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from backend.app.db.models import (
    Student,
    UserAccount,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.services.auth_service import (
    decode_access_token,
)


security = HTTPBearer(
    auto_error=False
)


# ============================================================
# CURRENT USER
# ============================================================


def get_current_user(

    credentials:
        HTTPAuthorizationCredentials
        | None
        = Depends(security),

    db: Session = Depends(get_db),

) -> UserAccount:

    if credentials is None:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Authentication required",

            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )


    token = credentials.credentials


    try:

        payload = (
            decode_access_token(
                token
            )
        )

        user_id = UUID(
            payload["sub"]
        )

    except (
        ValueError,
        KeyError,
    ):

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Invalid or expired token",

            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )


    user = db.get(
        UserAccount,
        user_id,
    )


    if (
        user is None
        or not user.is_active
    ):

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "User account not available",
        )


    return user


# ============================================================
# ROLE REQUIREMENT
# ============================================================


def require_roles(
    *allowed_roles: str,
):

    allowed = {
        role.upper()
        for role in allowed_roles
    }

    def dependency(

        current_user:
            UserAccount
            = Depends(
                get_current_user
            ),

    ) -> UserAccount:

        if (
            current_user.role
            not in allowed
        ):

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "You do not have permission "
                    "to access this resource"
                ),
            )

        return current_user


    return dependency


# ============================================================
# CURRENT STUDENT
# ============================================================


def get_current_student(

    current_user:
        UserAccount
        = Depends(
            require_roles(
                "STUDENT"
            )
        ),

    db: Session = Depends(
        get_db
    ),

) -> Student:

    if (
        current_user.student_id
        is None
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Student account is "
                "not linked to a student"
            ),
        )


    student = db.get(
        Student,
        current_user.student_id,
    )


    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )


    return student

def ensure_student_code_access(
    current_user: UserAccount,
    student_code: str,
    db: Session,
):

    # Faculty/admin may operate on
    # student records when appropriate.
    if current_user.role in {
        "FACULTY",
        "ADMIN",
    }:

        return


    if current_user.role != "STUDENT":

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    student = db.get(
        Student,
        current_user.student_id,
    )


    if (
        student is None
        or student.student_code
        != student_code
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You can only access "
                "your own student data"
            ),
        )
def ensure_learning_session_access(
    current_user: UserAccount,
    session,
):

    # Faculty/Admin can inspect sessions.
    if current_user.role in {
        "FACULTY",
        "ADMIN",
    }:

        return


    if current_user.role != "STUDENT":

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    if (
        current_user.student_id
        != session.student_id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot access "
                "another student's session"
            ),
        )

# ============================================================
# STUDENT CODE OWNERSHIP
# ============================================================


def ensure_student_code_access(
    current_user: UserAccount,
    student_code: str,
    db: Session,
):

    # Faculty/Admin may inspect student data.
    if current_user.role in {
        "FACULTY",
        "ADMIN",
    }:
        return


    if current_user.role != "STUDENT":

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    if current_user.student_id is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "Student account is not "
                "linked to a student"
            ),
        )


    student = db.get(
        Student,
        current_user.student_id,
    )


    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )


    if (
        student.student_code
        != student_code
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You can only access "
                "your own student data"
            ),
        )


# ============================================================
# LEARNING SESSION OWNERSHIP
# ============================================================


def ensure_learning_session_access(
    current_user: UserAccount,
    learning_session,
):

    # Faculty/Admin may inspect sessions.
    if current_user.role in {
        "FACULTY",
        "ADMIN",
    }:
        return


    if current_user.role != "STUDENT":

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    if current_user.student_id is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "Student account is not "
                "linked to a student"
            ),
        )


    if (
        current_user.student_id
        != learning_session.student_id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot access another "
                "student's learning session"
            ),
        )