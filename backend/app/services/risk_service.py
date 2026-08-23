from sqlalchemy.orm import Session

from backend.app.db.models import (
    InterventionTask,
    RiskInference,
    StudentFeatureSnapshot,
)

from backend.app.services.intervention_service import (
    generate_intervention,
)

from ml.predict import (
    MODEL_FEATURES,
    predict_student,
)


MODEL_VERSION = "sih-xgb-v1"


def evaluate_snapshot(
    db: Session,
    snapshot: StudentFeatureSnapshot,
):


    # ========================================================
    # 1. DATABASE SNAPSHOT → ML INPUT
    # ========================================================

    payload = {

        feature: getattr(
            snapshot,
            feature,
        )

        for feature
        in MODEL_FEATURES
    }


    # ========================================================
    # 2. RUN XGBOOST + SHAP
    # ========================================================

    ml_result = predict_student(
        payload
    )


    risk_score = float(
        ml_result[
            "risk_score"
        ]
    )

    risk_tier = ml_result[
        "risk_tier"
    ]


    # ========================================================
    # 3. SAVE ML INFERENCE
    # ========================================================

    inference = RiskInference(

        student_id=
            snapshot.student_id,

        snapshot_id=
            snapshot.snapshot_id,

        model_version=
            MODEL_VERSION,

        risk_score=
            risk_score,

        risk_tier=
            risk_tier,

        decision_threshold=
            0.50,

        predicted_dropout=
            risk_score >= 0.50,

        top_features=
            [],

        top_factors=
            ml_result[
                "top_risk_factors"
            ],
    )


    db.add(
        inference
    )

    db.commit()

    db.refresh(
        inference
    )


    # ========================================================
    # 4. SEND ML RESULT TO LANGGRAPH
    # ========================================================

    agent_result = (
        generate_intervention(

            student_id=str(
                snapshot.student_id
            ),

            ml_result=
                ml_result,
        )
    )


    intervention_id = None


    # ========================================================
    # 5. SAVE LANGGRAPH INTERVENTION
    # ========================================================

    if agent_result is not None:

        intervention = InterventionTask(

            student_id=
                snapshot.student_id,

            inference_id=
                inference.inference_id,

            routed_domain=
                agent_result[
                    "route"
                ],

            remediation_plan=
                agent_result[
                    "intervention_plan"
                ],

            outreach_message_draft=
                agent_result[
                    "outreach_message"
                ],

            status=
                "PENDING_REVIEW",
        )


        db.add(
            intervention
        )

        db.commit()

        db.refresh(
            intervention
        )


        intervention_id = str(
            intervention.task_id
        )


    # ========================================================
    # 6. FINAL API RESPONSE
    # ========================================================

    response = {

        "inference_id":
            str(
                inference.inference_id
            ),

        "student_id":
            str(
                snapshot.student_id
            ),

        "risk_score":
            risk_score,

        "risk_percentage":
            ml_result[
                "risk_percentage"
            ],

        "risk_tier":
            risk_tier,

        "top_risk_factors":
            ml_result[
                "top_risk_factors"
            ],

        "intervention":
            None,
    }


    if agent_result is not None:

        response[
            "intervention"
        ] = {

            "task_id":
                intervention_id,

            "route":
                agent_result[
                    "route"
                ],

            "plan":
                agent_result[
                    "intervention_plan"
                ],

            "outreach_message":
                agent_result[
                    "outreach_message"
                ],

            "review_status":
                "PENDING_REVIEW",
        }


    return response