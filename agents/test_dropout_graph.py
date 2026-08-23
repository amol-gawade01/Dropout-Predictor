from pprint import pprint

from agents.dropout_graph import (
    dropout_graph,
)


test_state = {

    "student_id":
        "SYN00001",

    "risk_score":
        0.6368,

    "risk_tier":
        "MODERATE",

    "top_risk_factors": [

       {
        "factor":
            "Financial Stress",

        "contribution_percentage":
            42.50,
    }
    ],

    "route":
        None,

    "intervention_plan":
        None,

    "outreach_message":
        None,
}


result = dropout_graph.invoke(
    test_state
)


print(
    "\nLANGGRAPH RESULT\n"
)

pprint(
    result
)