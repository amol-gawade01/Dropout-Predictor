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


from backend.app.core.auth import (
    require_roles,
)

from backend.app.services.faculty_insights_service import (
    get_faculty_at_risk_students,
    get_faculty_learning_overview,
    get_faculty_student_profile,
    get_misconception_insights,
    get_weak_concept_insights,
)

router = APIRouter(
    prefix="/faculty/learning",
    tags=["Faculty Learning Insights"],

    dependencies=[
        Depends(
            require_roles(
                "FACULTY",
                "ADMIN",
            )
        )
    ],
)


# ============================================================
# OVERVIEW
# ============================================================


@router.get("/overview")
def faculty_overview(
    db: Session = Depends(get_db),
):

    return (
        get_faculty_learning_overview(
            db
        )
    )


# ============================================================
# WEAK CONCEPTS
# ============================================================


@router.get("/weak-concepts")
def faculty_weak_concepts(

    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),

    db: Session = Depends(
        get_db
    ),
):

    return (
        get_weak_concept_insights(
            db=db,
            limit=limit,
        )
    )


# ============================================================
# MISCONCEPTIONS
# ============================================================


@router.get("/misconceptions")
def faculty_misconceptions(

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: Session = Depends(
        get_db
    ),
):

    return (
        get_misconception_insights(
            db=db,
            limit=limit,
        )
    )


# ============================================================
# AT-RISK STUDENTS
# ============================================================


@router.get("/at-risk-students")
def faculty_at_risk_students(

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),

    db: Session = Depends(
        get_db
    ),
):

    return (
        get_faculty_at_risk_students(
            db=db,
            limit=limit,
        )
    )


# ============================================================
# INDIVIDUAL STUDENT
# ============================================================


@router.get(
    "/student/{student_code}"
)
def faculty_student_profile(

    student_code: str,

    db: Session = Depends(
        get_db
    ),
):

    try:

        return (
            get_faculty_student_profile(
                db=db,
                student_code=
                    student_code,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc