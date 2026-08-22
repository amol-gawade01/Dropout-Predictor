import pandas as pd

# ==========================================
# 1. Load the actual ML dataset
# ==========================================

DATA_PATH = "dataset.xlsx"

df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)

print("=" * 60)
print("STUDENT DROPOUT DATASET - EDA")
print("=" * 60)


# ==========================================
# 2. Basic information
# ==========================================

print("\n1. DATASET SHAPE")
print(df.shape)


# ==========================================
# 3. Column names
# ==========================================

print("\n2. COLUMN NAMES")

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# ==========================================
# 4. Data types
# ==========================================

print("\n3. DATA TYPES")
print(df.dtypes)


# ==========================================
# 5. Missing values
# ==========================================

print("\n4. MISSING VALUES")

missing = df.isnull().sum()

missing = missing[
    missing > 0
].sort_values(
    ascending=False
)

print(missing)


# ==========================================
# 6. Duplicate rows
# ==========================================

print("\n5. DUPLICATE ROWS")

print(
    df.duplicated().sum()
)


# ==========================================
# 7. Target distribution
# ==========================================

print("\n6. DROPOUT TARGET DISTRIBUTION")

print(
    df["dropout_label"].value_counts()
)

print("\nTarget percentage:")

print(
    df["dropout_label"]
    .value_counts(
        normalize=True
    )
    * 100
)


# ==========================================
# 8. Train / validation / test split
# ==========================================

print("\n7. DATA SPLIT")

print(
    df["data_split"].value_counts()
)


# ==========================================
# 9. Student outcome
# ==========================================

print("\n8. STUDENT OUTCOME")

print(
    df["student_outcome"]
    .value_counts()
)


# ==========================================
# 10. Important numerical statistics
# ==========================================

print("\n9. NUMERICAL SUMMARY")

print(
    df.describe().T
)


print("\n" + "=" * 60)
print("EDA COMPLETE")
print("=" * 60)