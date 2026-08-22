import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier
from pathlib import Path


# ============================================================
# MODEL FEATURES
# ============================================================

MODEL_FEATURES = [

    # Academic
    "current_gpa",
    "failed_subjects",
    "backlog_count",
    "credits_completion_ratio",

    # Attendance
    "attendance_pct",
    "attendance_velocity_14d",
    "consecutive_absent_days",

    # Learning engagement
    "lms_active_hours_week",
    "lms_activity_velocity_pct",
    "assignment_completion_pct",
    "avg_assignment_delay_days",
    "missed_assessments",

    # Financial
    "fee_overdue_days",
    "scholarship_delay_days",
    "financial_support_requested",

    # Work
    "paid_work_hours_week",

    # Family
    "family_responsibility_hours_week",

    # Course mismatch
    "course_satisfaction_1_5",
    "career_uncertainty_1_5",

    # Transition
    "prerequisite_gap_score",
    "language_transition_score",

    # Commute / housing
    "commute_minutes_one_way",
    "hostel_issue_score",

    # Belonging
    "campus_belonging_1_5",
    "mentor_interactions_month",

    # Wellbeing
    "overwhelmed_score_1_5",
    "support_requested",
]


# ============================================================
# 11 RISK FACTORS
# ============================================================

RISK_FACTORS = {

    "Academic Difficulty": [
        "current_gpa",
        "failed_subjects",
        "backlog_count",
        "credits_completion_ratio",
    ],

    "Attendance Decline": [
        "attendance_pct",
        "attendance_velocity_14d",
        "consecutive_absent_days",
    ],

    "Low Learning Engagement": [
        "lms_active_hours_week",
        "lms_activity_velocity_pct",
        "assignment_completion_pct",
        "avg_assignment_delay_days",
        "missed_assessments",
    ],

    "Financial Stress": [
        "fee_overdue_days",
        "scholarship_delay_days",
        "financial_support_requested",
    ],

    "Employment / Work Pressure": [
        "paid_work_hours_week",
    ],

    "Family / Domestic Responsibility": [
        "family_responsibility_hours_week",
    ],

    "Course Mismatch / Low Interest": [
        "course_satisfaction_1_5",
        "career_uncertainty_1_5",
    ],

    "Transition / Language / Prerequisite Gap": [
        "prerequisite_gap_score",
        "language_transition_score",
    ],

    "Commute / Housing": [
        "commute_minutes_one_way",
        "hostel_issue_score",
    ],

    "Low Belonging / Weak Support": [
        "campus_belonging_1_5",
        "mentor_interactions_month",
    ],

    "Wellbeing / Support Need": [
        "overwhelmed_score_1_5",
        "support_requested",
    ],
}


# ============================================================
# LOAD MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "student_dropout_xgboost.json"
)


model = XGBClassifier()

model.load_model(
    MODEL_PATH
)
explainer = shap.TreeExplainer(model)


# ============================================================
# RISK TIER
# ============================================================

def get_risk_tier(risk_score):

    if risk_score >= 0.70:
        return "CRITICAL"

    elif risk_score >= 0.40:
        return "MODERATE"

    else:
        return "LOW"


# ============================================================
# PREDICT STUDENT
# ============================================================

def predict_student(student_data):

    """
    Takes one student's 27 ML features
    and returns a prediction dictionary.
    """

    # --------------------------------------------------------
    # Check missing features
    # --------------------------------------------------------

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in student_data
    ]

    if missing_features:

        raise ValueError(
            "Missing features: "
            + str(missing_features)
        )


    # --------------------------------------------------------
    # Create dataframe
    # --------------------------------------------------------

    X_student = pd.DataFrame(
        [
            {
                feature: student_data[feature]
                for feature in MODEL_FEATURES
            }
        ]
    )


    # --------------------------------------------------------
    # Predict probability
    # --------------------------------------------------------

    risk_score = float(
        model.predict_proba(
            X_student
        )[0][1]
    )


    # --------------------------------------------------------
    # Risk tier
    # --------------------------------------------------------

    risk_tier = get_risk_tier(
        risk_score
    )


    # --------------------------------------------------------
    # SHAP
    # --------------------------------------------------------

    shap_result = explainer(
        X_student
    )

    shap_values = (
        shap_result.values[0]
    )


    # --------------------------------------------------------
    # Calculate factor contributions
    # --------------------------------------------------------

    factor_results = []


    for factor_name, features in RISK_FACTORS.items():

        indices = [
            MODEL_FEATURES.index(feature)
            for feature in features
        ]

        contribution = float(
            np.sum(
                np.maximum(
                    shap_values[indices],
                    0
                )
            )
        )

        factor_results.append({

            "factor": factor_name,

            "contribution": contribution

        })


    # --------------------------------------------------------
    # Sort factors
    # --------------------------------------------------------

    factor_results.sort(
        key=lambda x: x["contribution"],
        reverse=True
    )


    # --------------------------------------------------------
    # Calculate percentages
    # --------------------------------------------------------

    total = sum(
        item["contribution"]
        for item in factor_results
    )


    if total > 0:

        for item in factor_results:

            item["contribution_percentage"] = round(
                (
                    item["contribution"]
                    / total
                ) * 100,
                2
            )

    else:

        for item in factor_results:

            item["contribution_percentage"] = 0


    # --------------------------------------------------------
    # Top 5 factors
    # --------------------------------------------------------

    top_factors = factor_results[:5]


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "risk_score": round(
            risk_score,
            4
        ),

        "risk_percentage": round(
            risk_score * 100,
            2
        ),

        "risk_tier": risk_tier,

        "top_risk_factors": top_factors,

    }