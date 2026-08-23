from backend.app.core.config import (
    get_settings,
)

from ml.data import load_dataset

from ml.predict import (
    MODEL_FEATURES,
)


LEAKAGE_COLUMNS = [
    "student_id",
    "data_split",

    "synthetic_risk_probability",
    "risk_tier",

    "dominant_risk_factor",
    "secondary_risk_factor",

    "dropout_label",

    "student_outcome",
    "confirmed_exit_reason",

    "generation_version",
]


def test_model_features_exist():

    settings = get_settings()

    df = load_dataset(
        settings.dataset_path
    )

    for feature in MODEL_FEATURES:
        assert feature in df.columns


def test_model_has_27_features():

    assert len(
        MODEL_FEATURES
    ) == 27


def test_no_leakage_columns_are_features():

    for column in LEAKAGE_COLUMNS:

        assert (
            column
            not in MODEL_FEATURES
        )