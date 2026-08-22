import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier


# ============================================================
# 1. DATASET
# ============================================================

DATA_PATH = "dataset.xlsx"


# ============================================================
# 2. MODEL FEATURES
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
# 3. RISK FACTOR GROUPS
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
# 4. LOAD DATA
# ============================================================

df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)


# ============================================================
# 5. LOAD TRAINED MODEL
# ============================================================

model = XGBClassifier()

model.load_model(
    "models/student_dropout_xgboost.json"
)

print("Model loaded successfully.")


# ============================================================
# 6. CREATE SHAP EXPLAINER
# ============================================================

explainer = shap.TreeExplainer(
    model
)


# ============================================================
# 7. SELECT A STUDENT
# ============================================================

student_id = input(
    "\nEnter student ID: "
).strip()


student_rows = df[
    df["student_id"].astype(str)
    == student_id
]


if student_rows.empty:

    print(
        f"\nStudent {student_id} not found."
    )

    exit()


student = student_rows.iloc[0]


# ============================================================
# 8. PREPARE STUDENT DATA
# ============================================================

X_student = pd.DataFrame(
    [
        [
            student[feature]
            for feature in MODEL_FEATURES
        ]
    ],
    columns=MODEL_FEATURES
)


# ============================================================
# 9. PREDICT RISK
# ============================================================

risk_probability = model.predict_proba(
    X_student
)[0][1]


risk_percentage = (
    risk_probability * 100
)


# ============================================================
# 10. RISK TIER
# ============================================================

if risk_probability >= 0.70:

    risk_tier = "CRITICAL"

elif risk_probability >= 0.40:

    risk_tier = "MODERATE"

else:

    risk_tier = "LOW"


# ============================================================
# 11. SHAP EXPLANATION
# ============================================================

shap_result = explainer(
    X_student
)

student_shap = (
    shap_result.values[0]
)


# ============================================================
# 12. CALCULATE RISK FACTOR CONTRIBUTIONS
# ============================================================

factor_results = []


for factor_name, features in RISK_FACTORS.items():

    indices = [
        MODEL_FEATURES.index(feature)
        for feature in features
    ]

    contribution = np.sum(
        np.maximum(
            student_shap[indices],
            0
        )
    )

    factor_results.append({

        "factor": factor_name,

        "contribution": contribution

    })


factor_df = pd.DataFrame(
    factor_results
)


# ============================================================
# 13. CONVERT TO PERCENTAGES
# ============================================================

total = factor_df[
    "contribution"
].sum()


if total > 0:

    factor_df[
        "percentage"
    ] = (
        factor_df["contribution"]
        / total
        * 100
    )

else:

    factor_df[
        "percentage"
    ] = 0


factor_df = factor_df.sort_values(
    "contribution",
    ascending=False
)


# ============================================================
# 14. DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 70)
print("STUDENT RISK ASSESSMENT")
print("=" * 70)

print(
    f"Student ID     : {student_id}"
)

print(
    f"Risk Score     : {risk_percentage:.2f}%"
)

print(
    f"Risk Tier      : {risk_tier}"
)


print("\n")
print("TOP RISK FACTORS")
print("-" * 70)


top_factors = factor_df.head(5)


for index, row in top_factors.iterrows():

    print(
        f"{row['factor']:<45}"
        f"{row['percentage']:>6.2f}%"
    )


print("\n")
print("=" * 70)
print("PREDICTION COMPLETE")
print("=" * 70)