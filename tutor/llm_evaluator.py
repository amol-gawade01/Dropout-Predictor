from typing import Literal

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from pydantic import (
    BaseModel,
    Field,
)

from backend.app.core.config import (
    get_settings,
)


class AnswerEvaluation(
    BaseModel
):

    is_correct: bool

    diagnosis: Literal[
        "CORRECT",
        "MINOR_ERROR",
        "CONCEPTUAL_MISUNDERSTANDING",
        "PREREQUISITE_GAP",
        "NO_ATTEMPT",
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    misconception: str | None = None

    reasoning_summary: str


settings = get_settings()


def get_evaluator():

    if not settings.google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing."
        )

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
    )

    return llm.with_structured_output(
        AnswerEvaluation,
        method="json_schema",
    )


def evaluate_answer(
    question: str,
    expected_answer: str,
    student_answer: str,
    mastery_prob: float,
) -> AnswerEvaluation:

    if not student_answer.strip():

        return AnswerEvaluation(
            is_correct=False,
            diagnosis="NO_ATTEMPT",
            confidence=1.0,
            misconception=None,
            reasoning_summary=(
                "Student did not provide "
                "an answer."
            ),
        )

    evaluator = get_evaluator()

    prompt = f"""
You are an educational answer evaluator.

Evaluate the student's answer based on meaning,
not exact wording.

Question:
{question}

Reference answer:
{expected_answer}

Student answer:
{student_answer}

Current mastery probability:
{mastery_prob:.2f}

Diagnosis rules:

CORRECT:
The answer is conceptually correct.

MINOR_ERROR:
The student understands the concept but made
a small error.

CONCEPTUAL_MISUNDERSTANDING:
The answer shows incorrect understanding of
the current concept.

PREREQUISITE_GAP:
The answer suggests the student may be missing
knowledge required before this concept.

NO_ATTEMPT:
No meaningful attempt was provided.

Do not mark an answer incorrect merely because
it uses different wording from the reference.
"""

    result = evaluator.invoke(
        prompt
    )

    return result