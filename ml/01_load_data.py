import pandas as pd

# Path to Excel dataset
DATA_PATH = "dataset.xlsx"

# Load the ML_Dataset sheet
df = pd.read_excel(
    DATA_PATH,
    sheet_name="ML_Dataset"
)

# Show first 5 student records
print("First 5 student records:")
print(df.head())

# Show dataset size
print("\nDataset shape:")
print(df.shape)

# Show column names
print("\nColumns:")
print(df.columns.tolist())