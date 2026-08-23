from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from backend.app.db.session import get_db

from backend.app.services.tutor_service import (
    process_tutor_attempt,
)


router = APIRouter(
    prefix="/tutor",
    tags=["Tutor"],
)


class TutorAttemptRequest(BaseModel):

    student_code: str

    concept_id: str

    student_answer: str

    is_correct: bool

    language_code: str = "en-IN"


@router.post("/attempt")
def submit_tutor_attempt(

    request: TutorAttemptRequest,

    db: Session = Depends(get_db),
):

    try:

        return process_tutor_attempt(

            db=db,

            student_code=
                request.student_code,

            concept_id=
                request.concept_id,

            student_answer=
                request.student_answer,

            is_correct=
                request.is_correct,

            language_code=
                request.language_code,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )