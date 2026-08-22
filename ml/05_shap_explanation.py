import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = "dataset.xlsx"

df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)


# ============================================================
# 2. DEFINE MODEL FEATURES
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

    # Engagement
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
# 3. LOAD TRAINED MODEL
# ============================================================

model = XGBClassifier()

model.load_model(
    "models/student_dropout_xgboost.json"
)

print("Model loaded successfully.")


# ============================================================
# 4. CREATE TEST DATA
# ============================================================

test_mask = (
    df["data_split"] == "TEST"
)

X_test = df.loc[
    test_mask,
    MODEL_FEATURES
].copy()

y_test = df.loc[
    test_mask,
    "dropout_label"
].copy()


print(
    "Test samples:",
    len(X_test)
)


# ============================================================
# 5. CREATE SHAP EXPLAINER
# ============================================================

print("\nCreating SHAP explainer...")

explainer = shap.TreeExplainer(
    model
)


# ============================================================
# 6. CALCULATE SHAP VALUES
# ============================================================

print("Calculating SHAP values...")

shap_values = explainer(
    X_test
)

print("SHAP calculation complete.")


# ============================================================
# 7. GLOBAL FEATURE IMPORTANCE
# ============================================================

# Mean absolute SHAP value tells us
# which features are most important overall.

mean_abs_shap = np.abs(
    shap_values.values
).mean(axis=0)


feature_importance = pd.DataFrame({

    "feature": MODEL_FEATURES,

    "mean_abs_shap":
        mean_abs_shap

})


feature_importance = (
    feature_importance
    .sort_values(
        "mean_abs_shap",
        ascending=False
    )
)


print("\n" + "=" * 60)
print("TOP GLOBAL RISK FEATURES")
print("=" * 60)

print(
    feature_importance
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 8. EXPLAIN ONE STUDENT
# ============================================================

student_index = 0

student = X_test.iloc[
    student_index
]

student_shap = (
    shap_values.values[
        student_index
    ]
)


explanation = pd.DataFrame({

    "feature": MODEL_FEATURES,

    "value": student.values,

    "shap_value": student_shap

})


# Only show features pushing risk upward.

risk_increasing = (
    explanation[
        explanation["shap_value"] > 0
    ]
    .sort_values(
        "shap_value",
        ascending=False
    )
)


print("\n" + "=" * 60)
print("WHY IS THIS STUDENT AT RISK?")
print("=" * 60)

print(
    risk_increasing
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 9. PREDICT THIS STUDENT'S RISK
# ============================================================

risk_probability = model.predict_proba(
    student.to_frame().T
)[0][1]


print("\nRisk probability:")

print(
    f"{risk_probability:.2%}"
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


print(
    "Risk tier:",
    risk_tier
)