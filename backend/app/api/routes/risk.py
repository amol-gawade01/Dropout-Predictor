from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import (
    Student,
    StudentFeatureSnapshot,
)
from backend.app.db.session import get_db
from backend.app.services.risk_service import (
    evaluate_snapshot,
)


router = APIRouter()


@router.post(
    "/risk/evaluate/{student_code}"
)
def evaluate_student(
    student_code: str,
    db: Session = Depends(
        get_db
    ),
):
    query = (
        select(
            StudentFeatureSnapshot
        )
        .join(
            Student,
            Student.student_id
            == StudentFeatureSnapshot.student_id,
        )
        .where(
            Student.student_code
            == student_code
        )
        .order_by(
            StudentFeatureSnapshot
            .week_start_date
            .desc()
        )
        .limit(1)
    )

    snapshot = (
        db.execute(
            query
        )
        .scalars()
        .first()
    )

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Student or feature "
                "snapshot not found."
            ),
        )

    try:
        result = evaluate_snapshot(
            db,
            snapshot,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "student_code":
            student_code,

        **result,
    }