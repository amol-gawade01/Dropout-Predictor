import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 1. LOAD DATASET
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

print("XGBoost model loaded successfully.")


# ============================================================
# 4. CREATE TEST DATA
# ============================================================

test_df = df[
    df["data_split"] == "TEST"
].copy()


X_test = test_df[
    MODEL_FEATURES
].copy()


y_test = test_df[
    "dropout_label"
].astype(int)


print(
    f"Test samples: {len(X_test)}"
)


# ============================================================
# 5. MAKE PREDICTIONS
# ============================================================

probabilities = model.predict_proba(
    X_test
)[:, 1]


# ------------------------------------------------------------
# IMPORTANT
# Use 0.50 first for standard model evaluation.
# Later we can tune this threshold specifically
# for the early-warning system.
# ------------------------------------------------------------

THRESHOLD = 0.50


predictions = (
    probabilities >= THRESHOLD
).astype(int)


# ============================================================
# 6. CALCULATE METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)


precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)


recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)


f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)


roc_auc = roc_auc_score(
    y_test,
    probabilities
)


pr_auc = average_precision_score(
    y_test,
    probabilities
)


# ============================================================
# 7. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    predictions
)


# ============================================================
# 8. PRINT RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("MODEL EVALUATION")
print("=" * 70)


print(
    f"\nAccuracy      : {accuracy:.4f}"
)


print(
    f"Precision     : {precision:.4f}"
)


print(
    f"Recall        : {recall:.4f}"
)


print(
    f"F1 Score      : {f1:.4f}"
)


print(
    f"ROC-AUC       : {roc_auc:.4f}"
)


print(
    f"PR-AUC        : {pr_auc:.4f}"
)


# ============================================================
# 9. CONFUSION MATRIX
# ============================================================

print("\n")
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(
    "\n                 Predicted"
)

print(
    "                 0       1"
)

print(
    f"Actual 0     {cm[0][0]:5d}  {cm[0][1]:5d}"
)

print(
    f"Actual 1     {cm[1][0]:5d}  {cm[1][1]:5d}"
)


# ============================================================
# 10. CLASSIFICATION REPORT
# ============================================================

print("\n")
print("=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Continued",
            "Dropout"
        ],
        zero_division=0
    )
)


# ============================================================
# 11. INTERPRETATION
# ============================================================

print("\n")
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)


print(
    "\nAccuracy tells us the overall percentage "
    "of correct predictions."
)


print(
    "Precision tells us how many students "
    "predicted as dropout were actually dropout."
)


print(
    "Recall tells us how many actual dropout-risk "
    "students the model successfully identified."
)


print(
    "F1 balances precision and recall."
)


print(
    "ROC-AUC measures how well the model "
    "separates the two classes."
)


print(
    "PR-AUC is particularly useful when "
    "the positive class is less common."
)


print("\n")
print("=" * 70)
print("EVALUATION COMPLETE")
print("=" * 70)