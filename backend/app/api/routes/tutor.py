from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    Student,
    StudentConceptMastery,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.schemas.tutor import (
    TutorAttemptRequest,
)

from backend.app.services.tutor_service import (
    process_tutor_attempt,
)


router = APIRouter(
    prefix="/tutor",
    tags=["Tutor"],
)


# ============================================================
# 1. LIST CONCEPTS
# ============================================================


@router.get("/concepts")
def list_concepts(
    db: Session = Depends(get_db),
):

    concepts = (
        db.query(Concept)
        .order_by(
            Concept.topic_name.asc()
        )
        .all()
    )

    return {

        "count":
            len(concepts),

        "concepts": [

            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "description":
                    concept
                    .concept_description,

                "prerequisite_concept_id":
                    concept
                    .prerequisite_concept_id,
            }

            for concept
            in concepts
        ],
    }


# ============================================================
# 2. STUDENT MASTERY MAP
# ============================================================


@router.get(
    "/mastery/{student_code}"
)
def mastery_map(

    student_code: str,

    db: Session = Depends(get_db),
):

    student = (
        db.query(Student)
        .filter(
            Student.student_code
            == student_code
        )
        .first()
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    concepts = (
        db.query(Concept)
        .order_by(
            Concept.topic_name.asc()
        )
        .all()
    )

    mastery_rows = (
        db.query(
            StudentConceptMastery
        )
        .filter(
            StudentConceptMastery.student_id
            == student.student_id
        )
        .all()
    )

    mastery_by_concept = {

        row.concept_id:
            row

        for row
        in mastery_rows
    }

    result = []

    for concept in concepts:

        row = mastery_by_concept.get(
            concept.concept_id
        )

        if row:

            mastery_prob = float(
                row.mastery_prob
            )

            attempts = (
                row.total_attempts
            )

            consecutive = (
                row.consecutive_correct
            )

        else:

            mastery_prob = 0.20
            attempts = 0
            consecutive = 0

        result.append(
            {

                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "prerequisite_concept_id":
                    concept
                    .prerequisite_concept_id,

                "mastery_probability":
                    mastery_prob,

                "mastery_percentage":
                    round(
                        mastery_prob
                        * 100,
                        2,
                    ),

                "mastered":
                    mastery_prob
                    >= 0.80,

                "total_attempts":
                    attempts,

                "consecutive_correct":
                    consecutive,
            }
        )

    return {

        "student_code":
            student.student_code,

        "concepts":
            result,
    }


# ============================================================
# 3. PROCESS TUTOR ATTEMPT
# ============================================================


@router.post("/attempt")
def submit_tutor_attempt(

    payload: TutorAttemptRequest,

    db: Session = Depends(get_db),
):

    try:

        return process_tutor_attempt(

            db=db,

            student_code=
                payload.student_code,

            concept_id=
                payload.concept_id,

            question=
                payload.question,

            student_answer=
                payload.student_answer,

            is_correct=
                payload.is_correct,

            language_code=
                payload.language_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc