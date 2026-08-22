from sqlalchemy.orm import Session

from backend.app.db.models import (
    RiskInference,
    StudentFeatureSnapshot,
)
from ml.features import MODEL_FEATURES
from ml.inference import RiskPredictor


_predictor = None


def get_predictor():
    global _predictor

    if _predictor is None:
        _predictor = RiskPredictor()

    return _predictor


def evaluate_snapshot(
    db: Session,
    snapshot: StudentFeatureSnapshot,
):
    predictor = get_predictor()

    payload = {
        feature: getattr(
            snapshot,
            feature,
        )
        for feature
        in MODEL_FEATURES
    }

    result = predictor.predict(
        payload
    )

    inference = RiskInference(

        student_id=
            snapshot.student_id,

        snapshot_id=
            snapshot.snapshot_id,

        model_version=
            result[
                "model_version"
            ],

        risk_score=
            result[
                "risk_score"
            ],

        risk_tier=
            result[
                "risk_tier"
            ],

        decision_threshold=
            result[
                "decision_threshold"
            ],

        predicted_dropout=
            result[
                "predicted_dropout"
            ],

        top_features=
            result[
                "top_features"
            ],

        top_factors=
            result[
                "top_factors"
            ],
    )

    db.add(inference)

    db.commit()

    db.refresh(inference)

    result[
        "inference_id"
    ] = str(
        inference.inference_id
    )

    return result