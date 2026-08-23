from agents.dropout_graph import (
    dropout_graph,
)


def generate_intervention(
    student_id: str,
    ml_result: dict,
) -> dict | None:

    risk_tier = ml_result[
        "risk_tier"
    ]


    # ========================================================
    # LOW RISK → no intervention
    # ========================================================

    if risk_tier == "LOW":

        return None


    # ========================================================
    # MODERATE / CRITICAL → LangGraph
    # ========================================================

    graph_input = {

        "student_id":
            student_id,

        "risk_score":
            ml_result[
                "risk_score"
            ],

        "risk_tier":
            risk_tier,

        "top_risk_factors":
            ml_result[
                "top_risk_factors"
            ],

        "route":
            None,

        "intervention_plan":
            None,

        "outreach_message":
            None,
    }


    result = dropout_graph.invoke(
        graph_input
    )


    return result