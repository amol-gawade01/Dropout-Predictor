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

class AdaptiveTutorAttemptRequest(
    BaseModel
):

    student_code: str = Field(
        min_length=1
    )

    question_id: str = Field(
        min_length=1
    )

    student_answer: str = ""

    language_code: str = (
        "en-IN"
    )

class StartLearningSessionRequest(
    BaseModel
):

    student_code: str = Field(
        min_length=1
    )

    concept_id: str = Field(
        min_length=1
    )

    target_questions: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    language_code: str = (
        "en-IN"
    )


class LearningSessionAnswerRequest(
    BaseModel
):

    question_id: str = Field(
        min_length=1
    )

    student_answer: str = ""


class EndLearningSessionRequest(
    BaseModel
):

    reason: str = (
        "STUDENT_ENDED"
    )