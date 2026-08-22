import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "dataset.xlsx"

df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)


# ============================================================
# 2. MODEL FEATURES
# ============================================================

MODEL_FEATURES = [

    # Factor 1 - Academic difficulty
    "current_gpa",
    "failed_subjects",
    "backlog_count",
    "credits_completion_ratio",

    # Factor 2 - Attendance decline
    "attendance_pct",
    "attendance_velocity_14d",
    "consecutive_absent_days",

    # Factor 3 - Learning engagement
    "lms_active_hours_week",
    "lms_activity_velocity_pct",
    "assignment_completion_pct",
    "avg_assignment_delay_days",
    "missed_assessments",

    # Factor 4 - Financial stress
    "fee_overdue_days",
    "scholarship_delay_days",
    "financial_support_requested",

    # Factor 5 - Work pressure
    "paid_work_hours_week",

    # Factor 6 - Family responsibility
    "family_responsibility_hours_week",

    # Factor 7 - Course mismatch
    "course_satisfaction_1_5",
    "career_uncertainty_1_5",

    # Factor 8 - Transition/language gap
    "prerequisite_gap_score",
    "language_transition_score",

    # Factor 9 - Commute/housing
    "commute_minutes_one_way",
    "hostel_issue_score",

    # Factor 10 - Belonging/support
    "campus_belonging_1_5",
    "mentor_interactions_month",

    # Factor 11 - Wellbeing/support need
    "overwhelmed_score_1_5",
    "support_requested",
]


# ============================================================
# 3. GROUP FEATURES INTO 11 RISK FACTORS
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
# 4. LOAD TRAINED XGBOOST MODEL
# ============================================================

model = XGBClassifier()

model.load_model(
    "models/student_dropout_xgboost.json"
)

print("XGBoost model loaded.")


# ============================================================
# 5. SELECT TEST DATA
# ============================================================

test_df = df[
    df["data_split"] == "TEST"
].copy()

X_test = test_df[
    MODEL_FEATURES
].copy()

print(
    "Test students:",
    len(X_test)
)


# ============================================================
# 6. CALCULATE SHAP VALUES
# ============================================================

print("\nCalculating SHAP values...")

explainer = shap.TreeExplainer(
    model
)

shap_result = explainer(
    X_test
)

shap_values = shap_result.values

print("SHAP calculation complete.")


# ============================================================
# 7. CALCULATE GLOBAL FACTOR IMPORTANCE
# ============================================================

factor_results = []

for factor_name, features in RISK_FACTORS.items():

    feature_indices = [
        MODEL_FEATURES.index(
            feature
        )
        for feature in features
    ]

    # Absolute SHAP = importance
    factor_shap = np.abs(
        shap_values[
            :,
            feature_indices
        ]
    ).mean()

    factor_results.append({

        "risk_factor": factor_name,

        "mean_shap_importance":
            factor_shap,

        "number_of_features":
            len(features)

    })


factor_df = pd.DataFrame(
    factor_results
)


# ============================================================
# 8. CALCULATE PERCENTAGE CONTRIBUTION
# ============================================================

total_importance = (
    factor_df[
        "mean_shap_importance"
    ].sum()
)

factor_df[
    "importance_percentage"
] = (
    factor_df[
        "mean_shap_importance"
    ]
    / total_importance
    * 100
)


factor_df = factor_df.sort_values(
    "mean_shap_importance",
    ascending=False
)


# ============================================================
# 9. DISPLAY RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("11 RISK FACTORS")
print("=" * 70)

print(
    factor_df[
        [
            "risk_factor",
            "mean_shap_importance",
            "importance_percentage",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# 10. SAVE GLOBAL FACTOR RESULTS
# ============================================================

factor_df.to_csv(
    "risk_factor_importance.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "risk_factor_importance.csv"
)


# ============================================================
# 11. EXPLAIN ONE STUDENT
# ============================================================

student_index = 0

student_shap = shap_values[
    student_index
]


student_factor_results = []


for factor_name, features in RISK_FACTORS.items():

    feature_indices = [
        MODEL_FEATURES.index(
            feature
        )
        for feature in features
    ]

    # Sum only positive SHAP values.
    # These are the features pushing
    # the prediction toward higher risk.

    contribution = np.sum(
        np.maximum(
            student_shap[
                feature_indices
            ],
            0
        )
    )

    student_factor_results.append({

        "risk_factor":
            factor_name,

        "risk_contribution":
            contribution

    })


student_factor_df = pd.DataFrame(
    student_factor_results
)


# ============================================================
# 12. CALCULATE STUDENT CONTRIBUTION %
# ============================================================

student_total = (
    student_factor_df[
        "risk_contribution"
    ].sum()
)


if student_total > 0:

    student_factor_df[
        "contribution_percentage"
    ] = (
        student_factor_df[
            "risk_contribution"
        ]
        / student_total
        * 100
    )

else:

    student_factor_df[
        "contribution_percentage"
    ] = 0


student_factor_df = (
    student_factor_df
    .sort_values(
        "risk_contribution",
        ascending=False
    )
)


# ============================================================
# 13. DISPLAY STUDENT RISK FACTORS
# ============================================================

print("\n")
print("=" * 70)
print("STUDENT-SPECIFIC RISK FACTORS")
print("=" * 70)

print(
    student_factor_df.to_string(
        index=False
    )
)


# ============================================================
# 14. SAVE STUDENT EXPLANATION
# ============================================================

student_factor_df.to_csv(
    "student_risk_factors.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "student_risk_factors.csv"
)


print("\n")
print("=" * 70)
print("RISK FACTOR ANALYSIS COMPLETE")
print("=" * 70)