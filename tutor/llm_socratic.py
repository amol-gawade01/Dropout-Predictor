from pydantic import BaseModel, Field

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from backend.app.core.config import (
    get_settings,
)


# ============================================================
# STRUCTURED RESPONSE
# ============================================================


class SocraticResponse(BaseModel):

    message: str = Field(
        description=(
            "Short tutor response that guides "
            "the student without directly giving "
            "the final answer."
        )
    )

    follow_up_question: str = Field(
        description=(
            "A question that makes the student "
            "reason about the concept."
        )
    )

    encouragement: str = Field(
        description=(
            "A short supportive sentence."
        )
    )


# ============================================================
# GEMINI
# ============================================================


def get_socratic_llm():

    settings = get_settings()

    if not settings.google_api_key:

        raise RuntimeError(
            "GOOGLE_API_KEY is missing."
        )

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
    )

    return llm.with_structured_output(
        SocraticResponse,
        method="json_schema",
    )


# ============================================================
# GENERATE SOCRATIC RESPONSE
# ============================================================


def generate_socratic_response(

    concept_name: str,

    question: str,

    student_answer: str,

    diagnosis: str,

    tutor_strategy: str,

    mastery_prob: float,

    misconception: str | None,

    prerequisite_name: str | None,

    language_code: str = "en-IN",
) -> SocraticResponse:

    llm = get_socratic_llm()

    language_map = {
        "en-IN": "English",
        "hi-IN": "Hindi",
        "mr-IN": "Marathi",
    }

    language = language_map.get(
        language_code,
        "English",
    )

    prompt = f"""
You are an adaptive Socratic tutor.

Your job is NOT to directly reveal the final answer.

Guide the student using questions, hints,
analogies, and reasoning.

Student context
----------------
Concept: {concept_name}

Question:
{question}

Student answer:
{student_answer}

Diagnosis:
{diagnosis}

Teaching strategy:
{tutor_strategy}

Current mastery:
{mastery_prob:.2f}

Detected misconception:
{misconception or "None"}

Prerequisite concept:
{prerequisite_name or "None"}

Response language:
{language}


TEACHING RULES
--------------

If strategy is CHALLENGE:
The student answered correctly.
Ask them to justify, generalize,
compare, or apply the concept.

If strategy is SMALL_NUDGE:
The student mostly understands.
Point toward the small mistake,
but do not reveal the answer.

If strategy is SOCRATIC_HINT:
Ask a question about the fundamental
property they may be misunderstanding.

If strategy is PREREQUISITE_SUPPORT:
Temporarily move attention toward
the prerequisite concept.

If strategy is GENTLE_START:
Give a very small starting hint
and ask an easy guiding question.

Always:
- Keep the response concise.
- Be supportive but not excessive.
- Do not give the complete solution.
- Ask exactly one meaningful
  follow-up question.
- Match the requested language.
"""

    return llm.invoke(
        prompt
    )