import pandas as pd

from predict import predict_student, MODEL_FEATURES


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_excel(
    "dataset.xlsx",
    sheet_name="ML_Dataset"
)


# ============================================================
# SELECT ONE STUDENT
# ============================================================

student_id = "SYN00001"

student_rows = df[
    df["student_id"].astype(str)
    == student_id
]


if student_rows.empty:

    raise ValueError(
        "Student not found."
    )


student = student_rows.iloc[0]


# ============================================================
# CREATE INPUT
# ============================================================

student_data = {

    feature: student[feature]

    for feature in MODEL_FEATURES

}


# ============================================================
# PREDICT
# ============================================================

result = predict_student(
    student_data
)


# ============================================================
# DISPLAY
# ============================================================

print("\n")
print("=" * 70)
print("ML PREDICTION")
print("=" * 70)

print(
    f"Student ID: {student_id}"
)

print(
    f"Risk Score: "
    f"{result['risk_percentage']}%"
)

print(
    f"Risk Tier: "
    f"{result['risk_tier']}"
)


print("\nTop Risk Factors:")

for factor in result[
    "top_risk_factors"
]:

    print(
        f"- {factor['factor']}: "
        f"{factor['contribution_percentage']}%"
    )


print("\n")
print("=" * 70)