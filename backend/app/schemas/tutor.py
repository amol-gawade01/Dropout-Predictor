from pydantic import (
    BaseModel,
    Field,
)


class TutorAttemptRequest(
    BaseModel
):

    student_code: str = Field(
        min_length=1
    )

    concept_id: str = Field(
        min_length=1
    )

    question: str = Field(
        min_length=1
    )

    student_answer: str = ""

    # Temporary for Phase 3.
    # Gemini will determine this
    # automatically in Phase 4.
    is_correct: bool

    language_code: str = (
        "en-IN"
    )