import pandas as pd


# ============================================================
# 1. LOAD DATASET
# ============================================================

DATA_PATH = "dataset.xlsx"

df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)

print("=" * 60)
print("PREPARING DATA FOR MACHINE LEARNING")
print("=" * 60)


# ============================================================
# 2. DEFINE MODEL FEATURES
# ============================================================
#
# These are the actual student signals that XGBoost
# will learn from.
#
# We are NOT using the F1-F11 factor scores as inputs.
# SHAP will later help us group raw features into
# these 11 factors.
# ============================================================

MODEL_FEATURES = [

    # --------------------------------------------------------
    # F1 - Academic difficulty
    # --------------------------------------------------------

    "current_gpa",
    "failed_subjects",
    "backlog_count",
    "credits_completion_ratio",

    # --------------------------------------------------------
    # F2 - Attendance decline
    # --------------------------------------------------------

    "attendance_pct",
    "attendance_velocity_14d",
    "consecutive_absent_days",

    # --------------------------------------------------------
    # F3 - Low learning engagement
    # --------------------------------------------------------

    "lms_active_hours_week",
    "lms_activity_velocity_pct",
    "assignment_completion_pct",
    "avg_assignment_delay_days",
    "missed_assessments",

    # --------------------------------------------------------
    # F4 - Financial stress
    # --------------------------------------------------------

    "fee_overdue_days",
    "scholarship_delay_days",
    "financial_support_requested",

    # --------------------------------------------------------
    # F5 - Employment/work pressure
    # --------------------------------------------------------

    "paid_work_hours_week",

    # --------------------------------------------------------
    # F6 - Family responsibility
    # --------------------------------------------------------

    "family_responsibility_hours_week",

    # --------------------------------------------------------
    # F7 - Course mismatch
    # --------------------------------------------------------

    "course_satisfaction_1_5",
    "career_uncertainty_1_5",

    # --------------------------------------------------------
    # F8 - Transition/language/prerequisite gap
    # --------------------------------------------------------

    "prerequisite_gap_score",
    "language_transition_score",

    # --------------------------------------------------------
    # F9 - Commute/housing
    # --------------------------------------------------------

    "commute_minutes_one_way",
    "hostel_issue_score",

    # --------------------------------------------------------
    # F10 - Belonging/support
    # --------------------------------------------------------

    "campus_belonging_1_5",
    "mentor_interactions_month",

    # --------------------------------------------------------
    # F11 - Wellbeing/support need
    # --------------------------------------------------------

    "overwhelmed_score_1_5",
    "support_requested",
]


TARGET = "dropout_label"


# ============================================================
# 3. CHECK THAT ALL FEATURES EXIST
# ============================================================

print("\nChecking model features...")

missing_features = [
    feature
    for feature in MODEL_FEATURES
    if feature not in df.columns
]

if missing_features:

    print(
        "ERROR: These features are missing:"
    )

    print(missing_features)

    raise ValueError(
        "Some model features are missing."
    )

print(
    "All model features are present."
)


# ============================================================
# 4. CREATE X AND y
# ============================================================

X = df[MODEL_FEATURES].copy()

y = df[TARGET].copy()


print("\nFeature matrix shape:")
print(X.shape)

print("\nTarget shape:")
print(y.shape)


# ============================================================
# 5. CHECK TARGET
# ============================================================

print("\nTarget distribution:")

print(
    y.value_counts()
)

print("\nTarget percentage:")

print(
    (y.value_counts(normalize=True) * 100)
    .round(2)
)


# ============================================================
# 6. CHECK DATA TYPES
# ============================================================

print("\nFeature data types:")

print(
    X.dtypes
)


# ============================================================
# 7. CHECK MISSING VALUES
# ============================================================

print("\nMissing values in model features:")

missing_values = X.isnull().sum()

print(
    missing_values[
        missing_values > 0
    ]
)

if X.isnull().sum().sum() == 0:

    print(
        "No missing values found."
    )


# ============================================================
# 8. CHECK TARGET VALUES
# ============================================================

print("\nUnique target values:")

print(
    sorted(y.unique())
)

if not set(y.unique()).issubset({0, 1}):

    raise ValueError(
        "Target must contain only 0 and 1."
    )


# ============================================================
# 9. USE THE PROVIDED TRAIN / VALID / TEST SPLIT
# ============================================================

print("\nSplitting dataset...")


train_mask = (
    df["data_split"] == "TRAIN"
)

valid_mask = (
    df["data_split"] == "VALID"
)

test_mask = (
    df["data_split"] == "TEST"
)


X_train = X[train_mask].copy()
y_train = y[train_mask].copy()

X_valid = X[valid_mask].copy()
y_valid = y[valid_mask].copy()

X_test = X[test_mask].copy()
y_test = y[test_mask].copy()


# ============================================================
# 10. PRINT SPLIT SIZES
# ============================================================

print("\nTRAIN:")
print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("\nVALIDATION:")
print("X_valid:", X_valid.shape)
print("y_valid:", y_valid.shape)

print("\nTEST:")
print("X_test:", X_test.shape)
print("y_test:", y_test.shape)


# ============================================================
# 11. CHECK TARGET DISTRIBUTION IN EACH SPLIT
# ============================================================

print("\nTarget distribution by split:")

print(
    "\nTRAIN:"
)

print(
    y_train.value_counts(
        normalize=True
    ).round(3)
)

print(
    "\nVALIDATION:"
)

print(
    y_valid.value_counts(
        normalize=True
    ).round(3)
)

print(
    "\nTEST:"
)

print(
    y_test.value_counts(
        normalize=True
    ).round(3)
)


# ============================================================
# 12. CHECK FOR DATA LEAKAGE
# ============================================================

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


leakage_used = [
    column
    for column in MODEL_FEATURES
    if column in LEAKAGE_COLUMNS
]


print("\nLeakage check:")

if leakage_used:

    print(
        "WARNING! Leakage columns found:"
    )

    print(leakage_used)

    raise ValueError(
        "Data leakage detected."
    )

else:

    print(
        "No leakage columns are being used."
    )


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)

print(
    "DATA PREPARATION COMPLETE"
)

print("=" * 60)

print(
    f"Number of features: {len(MODEL_FEATURES)}"
)

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Validation samples: {len(X_valid)}"
)

print(
    f"Test samples: {len(X_test)}"
)

print(
    "Target: dropout_label"
)

print(
    "Ready for XGBoost."
)

print("=" * 60)