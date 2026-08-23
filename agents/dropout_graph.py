from typing import TypedDict

from langgraph.graph import (
    END,
    START,
    StateGraph,
)


# ============================================================
# 1. LANGGRAPH STATE
# ============================================================


class DropoutState(TypedDict):

    student_id: str

    risk_score: float

    risk_tier: str

    top_risk_factors: list[dict]

    route: str | None

    intervention_plan: dict | None

    outreach_message: str | None


# ============================================================
# 2. TRIAGE NODE
# ============================================================


def triage_node(
    state: DropoutState,
) -> dict:

    factors = state[
        "top_risk_factors"
    ]

    # Fallback if SHAP returns no factors
    if not factors:

        return {
            "route": "academic"
        }

    top_factor = (
        factors[0]
        ["factor"]
        .lower()
    )

    # --------------------------------------------------------
    # Financial route
    # --------------------------------------------------------

    if (
        "financial" in top_factor
        or "work pressure" in top_factor
        or "employment" in top_factor
    ):

        route = "financial"


    # --------------------------------------------------------
    # Engagement route
    # --------------------------------------------------------

    elif (
        "engagement" in top_factor
        or "attendance" in top_factor
    ):

        route = "engagement"


    # --------------------------------------------------------
    # Welfare route
    # --------------------------------------------------------

    elif (
        "wellbeing" in top_factor
        or "belonging" in top_factor
        or "family" in top_factor
        or "domestic" in top_factor
    ):

        route = "welfare"


    # --------------------------------------------------------
    # Everything else → academic
    # --------------------------------------------------------

    else:

        route = "academic"


    return {
        "route": route
    }


# ============================================================
# 3. ACADEMIC SUPPORT NODE
# ============================================================


def academic_node(
    state: DropoutState,
) -> dict:

    plan = {

        "category":
            "ACADEMIC_SUPPORT",

        "priority":
            state["risk_tier"],

        "actions": [

            "Schedule faculty mentor meeting",

            "Identify difficult subjects",

            "Review failed subjects and backlogs",

            "Create targeted study plan",

            "Recommend peer tutoring or academic support",
        ],
    }

    return {
        "intervention_plan":
            plan
    }


# ============================================================
# 4. FINANCIAL SUPPORT NODE
# ============================================================


def financial_node(
    state: DropoutState,
) -> dict:

    plan = {

        "category":
            "FINANCIAL_SUPPORT",

        "priority":
            state["risk_tier"],

        "actions": [

            "Check scholarship eligibility",

            "Review scholarship delay",

            "Check pending fee status",

            "Provide fee instalment information",

            "Connect student with financial support office",
        ],
    }

    return {
        "intervention_plan":
            plan
    }


# ============================================================
# 5. ENGAGEMENT SUPPORT NODE
# ============================================================


def engagement_node(
    state: DropoutState,
) -> dict:

    plan = {

        "category":
            "ENGAGEMENT_SUPPORT",

        "priority":
            state["risk_tier"],

        "actions": [

            "Schedule attendance recovery meeting",

            "Review missed assignments",

            "Check recent LMS activity",

            "Create weekly learning targets",

            "Monitor engagement for the next two weeks",
        ],
    }

    return {
        "intervention_plan":
            plan
    }


# ============================================================
# 6. WELFARE / STUDENT SUPPORT NODE
# ============================================================


def welfare_node(
    state: DropoutState,
) -> dict:

    plan = {

        "category":
            "STUDENT_SUPPORT",

        "priority":
            state["risk_tier"],

        "actions": [

            "Schedule private mentor check-in",

            "Ask whether additional support is required",

            "Discuss workload or family constraints",

            "Offer campus support resources",

            "Offer counsellor referral when requested",
        ],
    }

    return {
        "intervention_plan":
            plan
    }


# ============================================================
# 7. COMMUNICATION NODE
# ============================================================


def communication_node(
    state: DropoutState,
) -> dict:

    risk_tier = state[
        "risk_tier"
    ]

    message = (
        "We noticed some changes in your recent "
        "academic engagement. Your faculty mentor "
        "would like to check in and understand "
        "whether you need any academic or personal "
        "support."
    )

    if risk_tier == "CRITICAL":

        message += (
            " We recommend arranging a mentor "
            "meeting as soon as possible."
        )

    elif risk_tier == "MODERATE":

        message += (
            " A short mentor discussion this week "
            "may help identify any difficulties early."
        )


    return {
        "outreach_message":
            message
    }


# ============================================================
# 8. BUILD THE GRAPH
# ============================================================


builder = StateGraph(
    DropoutState
)


# Add workflow nodes

builder.add_node(
    "triage",
    triage_node,
)

builder.add_node(
    "academic",
    academic_node,
)

builder.add_node(
    "financial",
    financial_node,
)

builder.add_node(
    "engagement",
    engagement_node,
)

builder.add_node(
    "welfare",
    welfare_node,
)

builder.add_node(
    "communication",
    communication_node,
)


# ============================================================
# 9. START → TRIAGE
# ============================================================


builder.add_edge(
    START,
    "triage",
)


# ============================================================
# 10. CONDITIONAL ROUTING
# ============================================================


builder.add_conditional_edges(

    "triage",

    lambda state:
        state["route"],

    {

        "academic":
            "academic",

        "financial":
            "financial",

        "engagement":
            "engagement",

        "welfare":
            "welfare",
    },
)


# ============================================================
# 11. SUPPORT NODE → COMMUNICATION
# ============================================================


builder.add_edge(
    "academic",
    "communication",
)

builder.add_edge(
    "financial",
    "communication",
)

builder.add_edge(
    "engagement",
    "communication",
)

builder.add_edge(
    "welfare",
    "communication",
)


# ============================================================
# 12. COMMUNICATION → END
# ============================================================


builder.add_edge(
    "communication",
    END,
)


# ============================================================
# 13. COMPILE GRAPH
# ============================================================


dropout_graph = (
    builder.compile()
)