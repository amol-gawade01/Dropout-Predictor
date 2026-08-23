from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from backend.app.db.session import (
    get_db,
)

from backend.app.services.student_dashboard_service import (
    build_student_dashboard,
    get_student_mastery_dashboard,
    get_student_mastery_trend,
    get_student_recent_activity,
)

from backend.app.core.auth import (
    get_current_student,
    require_roles,
)

from backend.app.db.models import (
    Student,
    UserAccount,
)

router = APIRouter(
    prefix="/student-dashboard",
    tags=["Student Dashboard"],
)

# ============================================================
# STUDENT'S OWN ROUTES - MUST COME FIRST
# ============================================================


@router.get("/me")
def my_student_dashboard(
    student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db),
):

    return build_student_dashboard(
        db=db,
        student_code=
            student.student_code,
    )


@router.get("/me/mastery")
def my_mastery(
    student: Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db),
):

    return get_student_mastery_dashboard(
        db=db,
        student_code=
            student.student_code,
    )


@router.get("/me/mastery-trend")
def my_mastery_trend(
    concept_id: str | None = None,

    student: Student = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db),
):

    return get_student_mastery_trend(
        db=db,
        student_code=
            student.student_code,
        concept_id=
            concept_id,
    )


@router.get("/me/recent-activity")
def my_recent_activity(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    student: Student = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db),
):

    return get_student_recent_activity(
        db=db,
        student_code=
            student.student_code,
        limit=limit,
    )


# ============================================================
# FACULTY / ADMIN ROUTES - MUST COME AFTER /me
# ============================================================


@router.get("/{student_code}")
def student_dashboard(
    student_code: str,

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    try:

        return build_student_dashboard(
            db=db,
            student_code=
                student_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("/{student_code}/mastery")
def student_mastery(
    student_code: str,

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    try:

        return get_student_mastery_dashboard(
            db=db,
            student_code=
                student_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("/{student_code}/mastery-trend")
def student_mastery_trend(
    student_code: str,
    concept_id: str | None = None,

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    try:

        return get_student_mastery_trend(
            db=db,
            student_code=
                student_code,
            concept_id=
                concept_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("/{student_code}/recent-activity")
def student_recent_activity(
    student_code: str,

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    try:

        return get_student_recent_activity(
            db=db,
            student_code=
                student_code,
            limit=limit,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc