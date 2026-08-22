import uuid
from datetime import date

import pandas as pd

from backend.app.core.config import get_settings
from backend.app.db.models import (
    Student,
    StudentFeatureSnapshot,
)
from backend.app.db.session import SessionLocal


settings = get_settings()


FACTOR_COLUMNS = [
    "F1_academic_difficulty",
    "F2_attendance_decline",
    "F3_low_engagement",
    "F4_financial_stress",
    "F5_work_pressure",
    "F6_family_responsibility",
    "F7_course_mismatch",
    "F8_transition_language_gap",
    "F9_commute_housing",
    "F10_low_belonging_support",
    "F11_wellbeing_support_need",
]


def safe_float(value):
    if pd.isna(value):
        return None

    return float(value)


def safe_int(value):
    if pd.isna(value):
        return 0

    return int(value)


def main():
    print(
        "Loading synthetic dataset..."
    )

    df = pd.read_excel(
        settings.dataset_path,
        sheet_name="ML_Dataset",
    )

    print(
        f"Rows found: {len(df)}"
    )

    db = SessionLocal()

    try:
        for index, row in df.iterrows():

            student_code = str(
                row["student_id"]
            )

            # Deterministic UUID means rerunning
            # the seed does not create duplicate students.
            student_uuid = uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"sih-student:{student_code}",
            )

            student = Student(
                student_id=student_uuid,

                student_code=student_code,

                display_name=(
                    "Demo Student "
                    + student_code[-5:]
                ),

                program_stream=str(
                    row["program_stream"]
                ),

                institution_type=str(
                    row["institution_type"]
                ),

                residence_mode=str(
                    row["residence_mode"]
                ),

                scholarship_holder=bool(
                    row[
                        "scholarship_holder"
                    ]
                ),

                preferred_language="en",

                is_synthetic=True,
            )

            db.merge(student)

            snapshot_uuid = uuid.uuid5(
                uuid.NAMESPACE_URL,
                (
                    f"sih-snapshot:"
                    f"{student_code}:"
                    "SIH_SYN_V1"
                ),
            )

            factor_scores = {
                column: safe_float(
                    row[column]
                )
                for column
                in FACTOR_COLUMNS
            }

            snapshot = (
                StudentFeatureSnapshot(

                    snapshot_id=
                        snapshot_uuid,

                    student_id=
                        student_uuid,

                    # Dataset v1 baseline week.
                    week_start_date=
                        date(
                            2026,
                            8,
                            17,
                        ),

                    semester=
                        safe_int(
                            row[
                                "semester"
                            ]
                        ),

                    # Factor 1
                    current_gpa=
                        safe_float(
                            row[
                                "current_gpa"
                            ]
                        ),

                    failed_subjects=
                        safe_int(
                            row[
                                "failed_subjects"
                            ]
                        ),

                    backlog_count=
                        safe_int(
                            row[
                                "backlog_count"
                            ]
                        ),

                    credits_completion_ratio=
                        safe_float(
                            row[
                                "credits_completion_ratio"
                            ]
                        ),

                    # Factor 2
                    attendance_pct=
                        safe_float(
                            row[
                                "attendance_pct"
                            ]
                        ),

                    attendance_velocity_14d=
                        safe_float(
                            row[
                                "attendance_velocity_14d"
                            ]
                        ),

                    consecutive_absent_days=
                        safe_int(
                            row[
                                "consecutive_absent_days"
                            ]
                        ),

                    # Factor 3
                    lms_active_hours_week=
                        safe_float(
                            row[
                                "lms_active_hours_week"
                            ]
                        ),

                    lms_activity_velocity_pct=
                        safe_float(
                            row[
                                "lms_activity_velocity_pct"
                            ]
                        ),

                    assignment_completion_pct=
                        safe_float(
                            row[
                                "assignment_completion_pct"
                            ]
                        ),

                    avg_assignment_delay_days=
                        safe_float(
                            row[
                                "avg_assignment_delay_days"
                            ]
                        ),

                    missed_assessments=
                        safe_int(
                            row[
                                "missed_assessments"
                            ]
                        ),

                    # Factor 4
                    fee_overdue_days=
                        safe_int(
                            row[
                                "fee_overdue_days"
                            ]
                        ),

                    scholarship_delay_days=
                        safe_int(
                            row[
                                "scholarship_delay_days"
                            ]
                        ),

                    financial_support_requested=
                        bool(
                            row[
                                "financial_support_requested"
                            ]
                        ),

                    # Factor 5
                    paid_work_hours_week=
                        safe_float(
                            row[
                                "paid_work_hours_week"
                            ]
                        ),

                    # Factor 6
                    family_responsibility_hours_week=
                        safe_float(
                            row[
                                "family_responsibility_hours_week"
                            ]
                        ),

                    # Factor 7
                    course_satisfaction_1_5=
                        safe_float(
                            row[
                                "course_satisfaction_1_5"
                            ]
                        ),

                    career_uncertainty_1_5=
                        safe_float(
                            row[
                                "career_uncertainty_1_5"
                            ]
                        ),

                    # Factor 8
                    prerequisite_gap_score=
                        safe_float(
                            row[
                                "prerequisite_gap_score"
                            ]
                        ),

                    language_transition_score=
                        safe_float(
                            row[
                                "language_transition_score"
                            ]
                        ),

                    # Factor 9
                    commute_minutes_one_way=
                        safe_int(
                            row[
                                "commute_minutes_one_way"
                            ]
                        ),

                    hostel_issue_score=
                        safe_float(
                            row[
                                "hostel_issue_score"
                            ]
                        ),

                    # Factor 10
                    campus_belonging_1_5=
                        safe_float(
                            row[
                                "campus_belonging_1_5"
                            ]
                        ),

                    mentor_interactions_month=
                        safe_int(
                            row[
                                "mentor_interactions_month"
                            ]
                        ),

                    # Factor 11
                    overwhelmed_score_1_5=
                        safe_float(
                            row[
                                "overwhelmed_score_1_5"
                            ]
                        ),

                    support_requested=
                        bool(
                            row[
                                "support_requested"
                            ]
                        ),

                    factor_scores=
                        factor_scores,

                    source=
                        "SYNTHETIC_SIH_V1",
                )
            )

            db.merge(snapshot)

            if (
                index + 1
            ) % 500 == 0:

                db.commit()

                print(
                    f"Imported "
                    f"{index + 1}"
                    f"/{len(df)}"
                )

        db.commit()

        print(
            "Synthetic dataset imported successfully."
        )

    except Exception:
        db.rollback()

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()