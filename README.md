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