from typing import Any
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
class StudentFeaturesRequest(BaseModel):

    student_id: str

    current_gpa: float
    failed_subjects: int
    backlog_count: int
    credits_completion_ratio: float

    attendance_pct: float
    attendance_velocity_14d: float
    consecutive_absent_days: int

    lms_active_hours_week: float
    lms_activity_velocity_pct: float
    assignment_completion_pct: float
    avg_assignment_delay_days: float
    missed_assessments: int

    fee_overdue_days: int
    scholarship_delay_days: int
    financial_support_requested: int

    paid_work_hours_week: float

    family_responsibility_hours_week: float

    course_satisfaction_1_5: float
    career_uncertainty_1_5: float

    prerequisite_gap_score: float
    language_transition_score: float

    commute_minutes_one_way: int
    hostel_issue_score: float

    campus_belonging_1_5: float
    mentor_interactions_month: int

    overwhelmed_score_1_5: float
    support_requested: int

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

@app.post("/predict-features")
def predict_from_features(
    request: StudentFeaturesRequest
):

    student_data = {

        "current_gpa":
            request.current_gpa,

        "failed_subjects":
            request.failed_subjects,

        "backlog_count":
            request.backlog_count,

        "credits_completion_ratio":
            request.credits_completion_ratio,

        "attendance_pct":
            request.attendance_pct,

        "attendance_velocity_14d":
            request.attendance_velocity_14d,

        "consecutive_absent_days":
            request.consecutive_absent_days,

        "lms_active_hours_week":
            request.lms_active_hours_week,

        "lms_activity_velocity_pct":
            request.lms_activity_velocity_pct,

        "assignment_completion_pct":
            request.assignment_completion_pct,

        "avg_assignment_delay_days":
            request.avg_assignment_delay_days,

        "missed_assessments":
            request.missed_assessments,

        "fee_overdue_days":
            request.fee_overdue_days,

        "scholarship_delay_days":
            request.scholarship_delay_days,

        "financial_support_requested":
            request.financial_support_requested,

        "paid_work_hours_week":
            request.paid_work_hours_week,

        "family_responsibility_hours_week":
            request.family_responsibility_hours_week,

        "course_satisfaction_1_5":
            request.course_satisfaction_1_5,

        "career_uncertainty_1_5":
            request.career_uncertainty_1_5,

        "prerequisite_gap_score":
            request.prerequisite_gap_score,

        "language_transition_score":
            request.language_transition_score,

        "commute_minutes_one_way":
            request.commute_minutes_one_way,

        "hostel_issue_score":
            request.hostel_issue_score,

        "campus_belonging_1_5":
            request.campus_belonging_1_5,

        "mentor_interactions_month":
            request.mentor_interactions_month,

        "overwhelmed_score_1_5":
            request.overwhelmed_score_1_5,

        "support_requested":
            request.support_requested
    }


    try:

        result = predict_student(
            student_data
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    return {

        "student_id":
            request.student_id,

        "risk_score":
            result["risk_score"],

        "risk_percentage":
            result["risk_percentage"],

        "risk_tier":
            result["risk_tier"],

        "top_risk_factors":
            result["top_risk_factors"]
    }
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