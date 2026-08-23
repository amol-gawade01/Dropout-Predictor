from tutor.question_bank import (
    get_questions_for_concept,
)


DIFFICULTY_ORDER = {
    "BEGINNER": [
        "BEGINNER",
        "INTERMEDIATE",
        "ADVANCED",
    ],

    "INTERMEDIATE": [
        "INTERMEDIATE",
        "BEGINNER",
        "ADVANCED",
    ],

    "ADVANCED": [
        "ADVANCED",
        "INTERMEDIATE",
        "BEGINNER",
    ],
}


def mastery_to_difficulty(
    mastery_prob: float,
) -> str:

    if mastery_prob < 0.35:
        return "BEGINNER"

    if mastery_prob < 0.75:
        return "INTERMEDIATE"

    return "ADVANCED"


def select_question(
    concept_id: str,
    mastery_prob: float,
    exclude_question_ids: set[str] | None = None,
):

    questions = get_questions_for_concept(
        concept_id
    )

    if not questions:
        return None

    excluded = (
        exclude_question_ids
        or set()
    )

    # Do not repeat questions already used
    # during the same learning session.
    available = [
        question
        for question in questions
        if question["question_id"]
        not in excluded
    ]

    if not available:
        return None

    desired_difficulty = (
        mastery_to_difficulty(
            mastery_prob
        )
    )

    # Try desired difficulty first,
    # then nearest available difficulty.
    for difficulty in (
        DIFFICULTY_ORDER[
            desired_difficulty
        ]
    ):

        for question in available:

            if (
                question["difficulty"]
                == difficulty
            ):
                return question

    return available[0]