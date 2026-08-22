from sqlalchemy.orm import Session

from backend.app.db.models import (
    RiskInference,
    StudentFeatureSnapshot,
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

    # --------------------------------------------------------
    # Convert database snapshot → ML input
    # --------------------------------------------------------

    payload = {
        feature: getattr(
            snapshot,
            feature,
        )
        for feature in MODEL_FEATURES
    }

    # --------------------------------------------------------
    # Run existing ML pipeline
    # --------------------------------------------------------

    result = predict_student(
        payload
    )

    risk_score = float(
        result["risk_score"]
    )

    # Your model already returns LOW/MODERATE/CRITICAL
    risk_tier = result[
        "risk_tier"
    ]

    # Keep binary prediction simple for now.
    predicted_dropout = (
        risk_score >= 0.50
    )

    # --------------------------------------------------------
    # Store inference
    # --------------------------------------------------------

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
            predicted_dropout,

        # Your current ML architecture returns
        # factor-level explanations, not raw top features.
        top_features=[],

        top_factors=
            result[
                "top_risk_factors"
            ],
    )

    db.add(inference)

    db.commit()

    db.refresh(inference)

    # --------------------------------------------------------
    # Backend response
    # --------------------------------------------------------

    return {
        "inference_id":
            str(
                inference.inference_id
            ),

        "student_id":
            str(
                snapshot.student_id
            ),

        "snapshot_id":
            str(
                snapshot.snapshot_id
            ),

        "model_version":
            MODEL_VERSION,

        "risk_score":
            risk_score,

        "risk_percentage":
            result[
                "risk_percentage"
            ],

        "risk_tier":
            risk_tier,

        "predicted_dropout":
            predicted_dropout,

        "decision_threshold":
            0.50,

        "top_risk_factors":
            result[
                "top_risk_factors"
            ],
    }