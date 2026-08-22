from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

from predict import predict_student, MODEL_FEATURES


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Student Dropout Risk Prediction API",
    description="ML API for the SIH Student Success Platform",
    version="1.0.0"
)


# ============================================================
# LOAD DATASET
# ============================================================

DATA_PATH = "dataset.csv"

df = pd.read_csv(DATA_PATH)


# ============================================================
# REQUEST MODEL
# ============================================================

class StudentRequest(BaseModel):

    student_id: str


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Student Risk Prediction API is running",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "XGBoost",
        "shap": "enabled"
    }


# ============================================================
# PREDICT STUDENT RISK
# ============================================================

@app.post("/predict")
def predict(request: StudentRequest):

    student_id = request.student_id

    # --------------------------------------------------------
    # Find student
    # --------------------------------------------------------

    student_rows = df[
        df["student_id"].astype(str)
        == student_id
    ]

    if student_rows.empty:

        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found."
        )

    student = student_rows.iloc[0]


    # --------------------------------------------------------
    # Create ML input
    # --------------------------------------------------------

    student_data = {

        feature: student[feature]

        for feature in MODEL_FEATURES

    }


    # --------------------------------------------------------
    # Run ML model
    # --------------------------------------------------------

    try:

        result = predict_student(
            student_data
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "student_id": student_id,

        "risk_score":
            result["risk_score"],

        "risk_percentage":
            result["risk_percentage"],

        "risk_tier":
            result["risk_tier"],

        "top_risk_factors":
            result["top_risk_factors"]

    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)