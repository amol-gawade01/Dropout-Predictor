from sqlalchemy.orm import Session

from backend.app.services.recommendation_service import (
    build_student_recommendations,
    get_latest_intervention,
)


def build_support_plan(
    db: Session,
    student_code: str,
):

    result = (
        build_student_recommendations(
            db=db,
            student_code=
                student_code,
            limit=3,
        )
    )

    student = result[
        "student"
    ]

    risk = result[
        "risk"
    ]

    intervention = (
        get_latest_intervention(
            db,
            student.student_id,
        )
    )


    # ========================================================
    # EWS INFORMATION
    # ========================================================

    ews = None

    if risk:

        ews = {

            "risk_score":
                float(
                    risk.risk_score
                ),

            "risk_percentage":
                round(
                    float(
                        risk.risk_score
                    )
                    * 100,
                    2,
                ),

            "risk_tier":
                risk.risk_tier,

            "top_factors":
                risk.top_factors,

            "academic_risk_factors":
                result[
                    "academic_risk_factors"
                ],

            "evaluated_at":
                risk.evaluated_at,
        }


    # ========================================================
    # FACULTY INTERVENTION
    # ========================================================

    intervention_data = None

    if intervention:

        intervention_data = {

            "task_id":
                str(
                    intervention.task_id
                ),

            "route":
                intervention
                .routed_domain,

            "status":
                intervention.status,

            "plan":
                intervention
                .remediation_plan,

            "mentor_notes":
                intervention
                .mentor_notes,

            "updated_at":
                intervention
                .updated_at,
        }


    # ========================================================
    # OVERALL ACTION
    # ========================================================

    risk_tier = (
        risk.risk_tier
        if risk
        else "UNKNOWN"
    )


    if risk_tier == "CRITICAL":

        overall_action = (
            "FACULTY_AND_TUTOR_SUPPORT"
        )

    elif risk_tier == "MODERATE":

        overall_action = (
            "TUTOR_AND_MONITOR"
        )

    else:

        overall_action = (
            "CONTINUE_PERSONALIZED_LEARNING"
        )


    return {

        "student": {

            "student_id":
                str(
                    student.student_id
                ),

            "student_code":
                student.student_code,

            "display_name":
                student.display_name,

            "program_stream":
                student.program_stream,

            "preferred_language":
                student
                .preferred_language,
        },

        "overall_action":
            overall_action,

        "ews":
            ews,

        "faculty_intervention":
            intervention_data,

        "tutor_recommendations":
            result[
                "recommendations"
            ],
    }