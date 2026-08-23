CORRECT = "CORRECT"

MINOR_ERROR = "MINOR_ERROR"

CONCEPTUAL_MISUNDERSTANDING = (
    "CONCEPTUAL_MISUNDERSTANDING"
)

PREREQUISITE_GAP = "PREREQUISITE_GAP"

NO_ATTEMPT = "NO_ATTEMPT"


def diagnose_attempt(
    student_answer: str,
    is_correct: bool,
    mastery_prob: float,
) -> str:

    answer = (student_answer or "").strip()

    if not answer:
        return NO_ATTEMPT

    if is_correct:
        return CORRECT

    if mastery_prob < 0.35:
        return PREREQUISITE_GAP

    if mastery_prob < 0.75:
        return CONCEPTUAL_MISUNDERSTANDING

    return MINOR_ERROR