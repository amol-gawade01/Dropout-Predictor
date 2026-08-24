from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import (
    RiskInference,
    Student,
    StudentFeatureSnapshot,
)
from backend.app.db.session import get_db
from backend.app.services.risk_service import (
    evaluate_snapshot,
)
from backend.app.core.auth import (
    require_roles,
)
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from backend.app.db.models import (
    InterventionTask,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.services.risk_service import (
    evaluate_snapshot,
)

router = APIRouter(
    prefix="/risk",
    tags=["Risk"],

    dependencies=[
        Depends(
            require_roles(
                "FACULTY",
                "ADMIN",
            )
        )
    ],
)


@router.post(
    "/evaluate-all",
    dependencies=[
        Depends(
            require_roles(
                "FACULTY",
                "ADMIN",
            )
        )
    ],
)
def evaluate_all_students(

    limit: int = Query(
        default=100,
        ge=1,
        le=5000,
    ),

    force: bool = Query(
        default=False
    ),

    db: Session = Depends(get_db),
):

    # ========================================================
    # GET ALL STUDENTS
    # ========================================================

    students = (
        db.query(Student)
        .limit(limit)
        .all()
    )


    evaluated = 0
    skipped = 0
    failed = 0

    results = []


    # ========================================================
    # PROCESS EACH STUDENT
    # ========================================================

    for student in students:

        try:

            # ------------------------------------------------
            # Find latest feature snapshot
            # ------------------------------------------------

            snapshot = (
                db.query(
                    StudentFeatureSnapshot
                )
                .filter(
                    StudentFeatureSnapshot.student_id
                    == student.student_id
                )
                .order_by(
                    StudentFeatureSnapshot
                    .week_start_date
                    .desc()
                )
                .first()
            )


            if snapshot is None:

                skipped += 1

                continue


            # ------------------------------------------------
            # Avoid evaluating same snapshot repeatedly
            # unless force=true
            # ------------------------------------------------

            existing = (
                db.query(RiskInference)
                .filter(
                    RiskInference.snapshot_id
                    == snapshot.snapshot_id
                )
                .first()
            )


            if (
                existing is not None
                and not force
            ):

                skipped += 1

                continue


            # ------------------------------------------------
            # ML → SHAP → LangGraph → DB
            # ------------------------------------------------

            result = evaluate_snapshot(
                db=db,
                snapshot=snapshot,
            )


            evaluated += 1


            results.append(
                {
                    "student_code":
                        student.student_code,

                    "risk_percentage":
                        result[
                            "risk_percentage"
                        ],

                    "risk_tier":
                        result[
                            "risk_tier"
                        ],
                }
            )


        except Exception as exc:

            failed += 1

            db.rollback()

            print(
                "Evaluation failed for",
                student.student_code,
                ":",
                exc,
            )


    return {

        "requested_students":
            len(students),

        "evaluated":
            evaluated,

        "skipped":
            skipped,

        "failed":
            failed,

        "results":
            results,
    }

@router.post(
    "/evaluate/{student_code}"
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

@router.patch(
    "/interventions/{task_id}/approve"
)
def approve_intervention(

    task_id: uuid.UUID,

    db: Session = Depends(
        get_db
    ),
):

    task = db.get(
        InterventionTask,
        task_id,
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail="Intervention not found",
        )


    task.status = "APPROVED"


    db.commit()

    db.refresh(
        task
    )


    return {

        "task_id":
            str(
                task.task_id
            ),

        "status":
            task.status,
    }

@router.patch(
    "/interventions/{task_id}/reject"
)
def reject_intervention(

    task_id: uuid.UUID,

    db: Session = Depends(
        get_db
    ),
):

    task = db.get(
        InterventionTask,
        task_id,
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail="Intervention not found",
        )


    task.status = "REJECTED"


    db.commit()

    db.refresh(
        task
    )


    return {

        "task_id":
            str(
                task.task_id
            ),

        "status":
            task.status,
    }