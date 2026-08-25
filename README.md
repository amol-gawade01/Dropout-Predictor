# Student Dropout Risk Prediction — ML

## Overview

This folder contains the Machine Learning component of the
AI-powered Student Success Platform.

The model predicts a student's dropout risk and identifies
the major predictive risk factors.

## ML Pipeline

Dataset
→ Data Preparation
→ XGBoost
→ Model Evaluation
→ SHAP Explainability
→ Risk Factor Analysis
→ Student Prediction
→ FastAPI

## Risk Factors

The model covers 11 major risk dimensions:

1. Academic Difficulty
2. Attendance Decline
3. Low Learning Engagement
4. Financial Stress
5. Employment / Work Pressure
6. Family / Domestic Responsibility
7. Course Mismatch / Low Interest
8. Transition / Language / Prerequisite Gap
9. Commute / Housing
10. Low Belonging / Weak Support
11. Wellbeing / Support Need

## Model

Algorithm:

XGBoost Classifier

Explainability:

SHAP

The model produces:

- Dropout risk score
- Risk percentage
- Risk tier
- Top predictive risk factors

## Risk Tiers

| Risk Score | Risk Tier |
|------------|-----------|
| 0.00–0.39 | LOW |
| 0.40–0.69 | MODERATE |
| 0.70–1.00 | CRITICAL |

## Dataset

The current prototype uses a synthetic student dataset.

Therefore, the current results demonstrate prototype functionality
and should not be interpreted as real-world dropout prediction
accuracy.

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## Backend development server

Start FastAPI with automatic reload from the repository root:

```bash
uv run python -m backend.dev
```

The API runs at `http://127.0.0.1:8000`, and Swagger is at `http://127.0.0.1:8000/docs`. Changes in `backend/`, `agents/`, `tutor/`, or `ml/` restart the local server. Do not use this reload command as the Render production start command.
