from typing import TypedDict

from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from tutor.bkt import update_mastery

from tutor.diagnostic import (
    CONCEPTUAL_MISUNDERSTANDING,
    CORRECT,
    MINOR_ERROR,
    NO_ATTEMPT,
    PREREQUISITE_GAP,
    diagnose_attempt,
)


# ============================================================
# STATE
# ============================================================


class TutorState(TypedDict):

    student_id: str

    concept_id: str

    prerequisite_concept_id: str | None

    question: str

    student_answer: str

    is_correct: bool

    mastery_before: float

    diagnosis: str | None

    route: str | None

    tutor_strategy: str | None

    tutor_message: str | None

    mastery_after: float | None


# ============================================================
# DIAGNOSE STUDENT ATTEMPT
# ============================================================


def diagnose_node(
    state: TutorState,
) -> dict:

    diagnosis = diagnose_attempt(
        student_answer=
            state["student_answer"],

        is_correct=
            state["is_correct"],

        mastery_prob=
            state["mastery_before"],
    )

    route_map = {

        CORRECT:
            "challenge",

        MINOR_ERROR:
            "nudge",

        CONCEPTUAL_MISUNDERSTANDING:
            "socratic_hint",

        PREREQUISITE_GAP:
            "prerequisite",

        NO_ATTEMPT:
            "gentle_start",
    }

    return {
        "diagnosis":
            diagnosis,

        "route":
            route_map[diagnosis],
    }


# ============================================================
# CORRECT ANSWER
# ============================================================


def challenge_node(
    state: TutorState,
) -> dict:

    return {

        "tutor_strategy":
            "CHALLENGE",

        "tutor_message": (
            "Good. Now explain why your "
            "answer is correct in your own "
            "words. Which principle supports it?"
        ),
    }


# ============================================================
# MINOR ERROR
# ============================================================


def nudge_node(
    state: TutorState,
) -> dict:

    return {

        "tutor_strategy":
            "SMALL_NUDGE",

        "tutor_message": (
            "You are close. Recheck the step "
            "where you applied the rule. "
            "What assumption did you make?"
        ),
    }


# ============================================================
# CONCEPTUAL MISUNDERSTANDING
# ============================================================


def socratic_hint_node(
    state: TutorState,
) -> dict:

    return {

        "tutor_strategy":
            "SOCRATIC_HINT",

        "tutor_message": (
            "Think about the basic definition "
            "of this concept. Which property "
            "must always remain true?"
        ),
    }


# ============================================================
# PREREQUISITE GAP
# ============================================================


def prerequisite_node(
    state: TutorState,
) -> dict:

    prerequisite = state[
        "prerequisite_concept_id"
    ]

    if prerequisite:

        message = (
            "Before continuing, let's revisit "
            f"the prerequisite concept: {prerequisite}. "
            "What do you remember about it?"
        )

    else:

        message = (
            "Let's return to the fundamentals. "
            "Can you explain the main idea of "
            "this concept in simple words?"
        )

    return {

        "tutor_strategy":
            "PREREQUISITE_SUPPORT",

        "tutor_message":
            message,
    }


# ============================================================
# NO ATTEMPT
# ============================================================


def gentle_start_node(
    state: TutorState,
) -> dict:

    return {

        "tutor_strategy":
            "GENTLE_START",

        "tutor_message": (
            "Start by telling me which part "
            "of the question seems unclear. "
            "We can work from there."
        ),
    }


# ============================================================
# UPDATE BKT MASTERY
# ============================================================


def update_mastery_node(
    state: TutorState,
) -> dict:

    new_mastery = update_mastery(

        prior_mastery=
            state["mastery_before"],

        correct=
            state["is_correct"],
    )

    return {
        "mastery_after":
            new_mastery
    }


# ============================================================
# BUILD GRAPH
# ============================================================


builder = StateGraph(
    TutorState
)


builder.add_node(
    "diagnose",
    diagnose_node,
)

builder.add_node(
    "challenge",
    challenge_node,
)

builder.add_node(
    "nudge",
    nudge_node,
)

builder.add_node(
    "socratic_hint",
    socratic_hint_node,
)

builder.add_node(
    "prerequisite",
    prerequisite_node,
)

builder.add_node(
    "gentle_start",
    gentle_start_node,
)

builder.add_node(
    "update_mastery",
    update_mastery_node,
)


# ============================================================
# START
# ============================================================


builder.add_edge(
    START,
    "diagnose",
)


# ============================================================
# CONDITIONAL ROUTING
# ============================================================


builder.add_conditional_edges(

    "diagnose",

    lambda state:
        state["route"],

    {
        "challenge":
            "challenge",

        "nudge":
            "nudge",

        "socratic_hint":
            "socratic_hint",

        "prerequisite":
            "prerequisite",

        "gentle_start":
            "gentle_start",
    },
)


# ============================================================
# EVERY TEACHING NODE → BKT
# ============================================================


for node in [

    "challenge",
    "nudge",
    "socratic_hint",
    "prerequisite",
    "gentle_start",

]:

    builder.add_edge(
        node,
        "update_mastery",
    )


# ============================================================
# BKT → END
# ============================================================


builder.add_edge(
    "update_mastery",
    END,
)


# ============================================================
# COMPILE
# ============================================================


tutor_graph = (
    builder.compile()
)