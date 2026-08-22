import pandas as pd
import numpy as np

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
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
# 2. DEFINE FEATURES
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

    # Transition / language
    "prerequisite_gap_score",
    "language_transition_score",

    # Commute / housing
    "commute_minutes_one_way",
    "hostel_issue_score",

    # Belonging / support
    "campus_belonging_1_5",
    "mentor_interactions_month",

    # Wellbeing
    "overwhelmed_score_1_5",
    "support_requested",
]

TARGET = "dropout_label"


# ============================================================
# 3. CREATE X AND y
# ============================================================

X = df[MODEL_FEATURES].copy()
y = df[TARGET].copy()


# ============================================================
# 4. USE PROVIDED TRAIN / VALID / TEST SPLITS
# ============================================================

train_mask = df["data_split"] == "TRAIN"
valid_mask = df["data_split"] == "VALID"
test_mask = df["data_split"] == "TEST"


X_train = X[train_mask]
y_train = y[train_mask]

X_valid = X[valid_mask]
y_valid = y[valid_mask]

X_test = X[test_mask]
y_test = y[test_mask]


print("=" * 60)
print("XGBOOST STUDENT DROPOUT MODEL")
print("=" * 60)

print("\nTraining samples:", len(X_train))
print("Validation samples:", len(X_valid))
print("Test samples:", len(X_test))


# ============================================================
# 5. CHECK CLASS BALANCE
# ============================================================

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = (
    negative_count / positive_count
)

print("\nTraining class distribution:")

print("Continued:", negative_count)
print("Dropout:", positive_count)

print(
    "Scale positive weight:",
    round(scale_pos_weight, 3)
)


# ============================================================
# 6. CREATE XGBOOST MODEL
# ============================================================

model = XGBClassifier(

    objective="binary:logistic",

    eval_metric="auc",

    n_estimators=300,

    max_depth=4,

    learning_rate=0.05,

    min_child_weight=3,

    subsample=0.85,

    colsample_bytree=0.85,

    reg_alpha=0.1,

    reg_lambda=1.5,

    scale_pos_weight=scale_pos_weight,

    tree_method="hist",

    random_state=42,

    n_jobs=-1,
)


# ============================================================
# 7. TRAIN MODEL
# ============================================================

print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train
)

print("Training complete!")


# ============================================================
# 8. VALIDATION PREDICTIONS
# ============================================================

valid_probabilities = model.predict_proba(
    X_valid
)[:, 1]

valid_predictions = (
    valid_probabilities >= 0.50
).astype(int)


# ============================================================
# 9. VALIDATION METRICS
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print(
    "Accuracy:",
    round(
        accuracy_score(
            y_valid,
            valid_predictions
        ),
        4
    )
)

print(
    "Precision:",
    round(
        precision_score(
            y_valid,
            valid_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "Recall:",
    round(
        recall_score(
            y_valid,
            valid_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "F1 Score:",
    round(
        f1_score(
            y_valid,
            valid_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "ROC-AUC:",
    round(
        roc_auc_score(
            y_valid,
            valid_probabilities
        ),
        4
    )
)


# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_valid,
        valid_predictions
    )
)


# ============================================================
# 11. TEST SET EVALUATION
# ============================================================

test_probabilities = model.predict_proba(
    X_test
)[:, 1]

test_predictions = (
    test_probabilities >= 0.50
).astype(int)


print("\n" + "=" * 60)
print("TEST RESULTS")
print("=" * 60)

print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            test_predictions
        ),
        4
    )
)

print(
    "Precision:",
    round(
        precision_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "Recall:",
    round(
        recall_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "F1 Score:",
    round(
        f1_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        4
    )
)

print(
    "ROC-AUC:",
    round(
        roc_auc_score(
            y_test,
            test_probabilities
        ),
        4
    )
)


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({

    "feature": MODEL_FEATURES,

    "importance": model.feature_importances_

})

importance = importance.sort_values(
    "importance",
    ascending=False
)


print("\n" + "=" * 60)
print("TOP 10 FEATURE IMPORTANCES")
print("=" * 60)

print(
    importance.head(10).to_string(
        index=False
    )
)


# ============================================================
# 13. SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 60)
print("SAMPLE PREDICTIONS")
print("=" * 60)

for i in range(10):

    print(
        f"Student {i + 1}: "
        f"Actual={y_test.iloc[i]} | "
        f"Risk Probability="
        f"{test_probabilities[i]:.3f}"
    )


print("\n" + "=" * 60)
print("MODEL TRAINING COMPLETE")
print("=" * 60)
# ============================================================
# 14. SAVE TRAINED MODEL
# ============================================================

import os

os.makedirs("models", exist_ok=True)

model.save_model(
    "models/student_dropout_xgboost.json"
)

print("\nModel saved successfully!")
print(
    "Location: models/student_dropout_xgboost.json"
)