from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import (
    InterventionTask,
    RiskInference,
    Student,
    StudentFeatureSnapshot,
)
from backend.app.db.session import get_db


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# HELPER
# Get the most recent inference time for every student.
# ============================================================


def latest_inference_subquery():

    return (
        select(
            RiskInference.student_id,
            func.max(
                RiskInference.evaluated_at
            ).label(
                "latest_evaluated_at"
            ),
        )
        .group_by(
            RiskInference.student_id
        )
        .subquery()
    )


# ============================================================
# 1. DASHBOARD SUMMARY
# ============================================================


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
):

    latest = (
        latest_inference_subquery()
    )

    latest_inferences = (
        db.query(RiskInference)
        .join(
            latest,
            (
                RiskInference.student_id
                == latest.c.student_id
            )
            & (
                RiskInference.evaluated_at
                == latest.c.latest_evaluated_at
            ),
        )
        .all()
    )

    low = 0
    moderate = 0
    critical = 0

    for inference in latest_inferences:

        if inference.risk_tier == "LOW":
            low += 1

        elif (
            inference.risk_tier
            == "MODERATE"
        ):
            moderate += 1

        elif (
            inference.risk_tier
            == "CRITICAL"
        ):
            critical += 1

    total_students = (
        db.query(Student)
        .count()
    )

    pending_interventions = (
        db.query(InterventionTask)
        .filter(
            InterventionTask.status
            == "PENDING_REVIEW"
        )
        .count()
    )

    approved_interventions = (
        db.query(InterventionTask)
        .filter(
            InterventionTask.status
            == "APPROVED"
        )
        .count()
    )

    rejected_interventions = (
        db.query(InterventionTask)
        .filter(
            InterventionTask.status
            == "REJECTED"
        )
        .count()
    )

    return {
        "total_students":
            total_students,

        "students_evaluated":
            len(latest_inferences),

        "low_risk_students":
            low,

        "moderate_risk_students":
            moderate,

        "critical_risk_students":
            critical,

        "pending_interventions":
            pending_interventions,

        "approved_interventions":
            approved_interventions,

        "rejected_interventions":
            rejected_interventions,
    }


# ============================================================
# 2. AT-RISK STUDENTS
# ============================================================


@router.get("/at-risk")
def get_at_risk_students(

    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),

    db: Session = Depends(get_db),
):

    latest = (
        latest_inference_subquery()
    )

    rows = (
        db.query(
            Student,
            RiskInference,
        )
        .join(
            RiskInference,
            RiskInference.student_id
            == Student.student_id,
        )
        .join(
            latest,
            (
                RiskInference.student_id
                == latest.c.student_id
            )
            & (
                RiskInference.evaluated_at
                == latest.c.latest_evaluated_at
            ),
        )
        .filter(
            RiskInference.risk_tier.in_(
                [
                    "MODERATE",
                    "CRITICAL",
                ]
            )
        )
        .order_by(
            RiskInference
            .risk_score
            .desc()
        )
        .limit(limit)
        .all()
    )

    students = []

    for student, inference in rows:

        top_factor = None
        top_factor_percentage = None

        if (
            inference.top_factors
            and len(
                inference.top_factors
            ) > 0
        ):

            first_factor = (
                inference.top_factors[0]
            )

            top_factor = (
                first_factor.get(
                    "factor"
                )
            )

            top_factor_percentage = (
                first_factor.get(
                    "contribution_percentage"
                )
            )

        students.append(
            {
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

                "risk_score":
                    float(
                        inference.risk_score
                    ),

                "risk_percentage":
                    round(
                        float(
                            inference.risk_score
                        )
                        * 100,
                        2,
                    ),

                "risk_tier":
                    inference.risk_tier,

                "top_factor":
                    top_factor,

                "top_factor_percentage":
                    top_factor_percentage,

                "evaluated_at":
                    inference.evaluated_at,
            }
        )

    return {
        "count":
            len(students),

        "students":
            students,
    }


# ============================================================
# 3. STUDENT DETAILS
# ============================================================


@router.get(
    "/student/{student_code}"
)
def student_details(

    student_code: str,

    db: Session = Depends(get_db),
):

    student = (
        db.query(Student)
        .filter(
            Student.student_code
            == student_code
        )
        .first()
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    # --------------------------------------------------------
    # Latest feature snapshot
    # --------------------------------------------------------

    latest_snapshot = (
        db.query(
            StudentFeatureSnapshot
        )
        .filter(
            StudentFeatureSnapshot.student_id
            == student.student_id
        )
        .order_by(
            StudentFeatureSnapshot
            .week_start_date
            .desc()
        )
        .first()
    )

    # --------------------------------------------------------
    # Latest risk prediction
    # --------------------------------------------------------

    latest_inference = (
        db.query(RiskInference)
        .filter(
            RiskInference.student_id
            == student.student_id
        )
        .order_by(
            RiskInference
            .evaluated_at
            .desc()
        )
        .first()
    )

    # --------------------------------------------------------
    # Latest intervention
    # --------------------------------------------------------

    latest_intervention = (
        db.query(
            InterventionTask
        )
        .filter(
            InterventionTask.student_id
            == student.student_id
        )
        .order_by(
            InterventionTask
            .updated_at
            .desc()
        )
        .first()
    )

    response = {

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

            "institution_type":
                student.institution_type,

            "residence_mode":
                student.residence_mode,

            "scholarship_holder":
                student.scholarship_holder,

            "preferred_language":
                student.preferred_language,
        },

        "latest_snapshot":
            None,

        "risk":
            None,

        "intervention":
            None,
    }

    # --------------------------------------------------------
    # Snapshot response
    # --------------------------------------------------------

    if latest_snapshot:

        response[
            "latest_snapshot"
        ] = {

            "snapshot_id":
                str(
                    latest_snapshot.snapshot_id
                ),

            "semester":
                latest_snapshot.semester,

            "week_start_date":
                latest_snapshot.week_start_date,

            "current_gpa":
                latest_snapshot.current_gpa,

            "failed_subjects":
                latest_snapshot.failed_subjects,

            "backlog_count":
                latest_snapshot.backlog_count,

            "attendance_pct":
                latest_snapshot.attendance_pct,

            "attendance_velocity_14d":
                latest_snapshot
                .attendance_velocity_14d,

            "assignment_completion_pct":
                latest_snapshot
                .assignment_completion_pct,

            "lms_active_hours_week":
                latest_snapshot
                .lms_active_hours_week,

            "fee_overdue_days":
                latest_snapshot
                .fee_overdue_days,

            "overwhelmed_score_1_5":
                latest_snapshot
                .overwhelmed_score_1_5,
        }

    # --------------------------------------------------------
    # Risk response
    # --------------------------------------------------------

    if latest_inference:

        response[
            "risk"
        ] = {

            "inference_id":
                str(
                    latest_inference
                    .inference_id
                ),

            "model_version":
                latest_inference
                .model_version,

            "risk_score":
                float(
                    latest_inference
                    .risk_score
                ),

            "risk_percentage":
                round(
                    float(
                        latest_inference
                        .risk_score
                    )
                    * 100,
                    2,
                ),

            "risk_tier":
                latest_inference
                .risk_tier,

            "top_risk_factors":
                latest_inference
                .top_factors,

            "evaluated_at":
                latest_inference
                .evaluated_at,
        }

    # --------------------------------------------------------
    # Intervention response
    # --------------------------------------------------------

    if latest_intervention:

        response[
            "intervention"
        ] = {

            "task_id":
                str(
                    latest_intervention
                    .task_id
                ),

            "route":
                latest_intervention
                .routed_domain,

            "plan":
                latest_intervention
                .remediation_plan,

            "outreach_message":
                latest_intervention
                .outreach_message_draft,

            "status":
                latest_intervention
                .status,

            "mentor_notes":
                latest_intervention
                .mentor_notes,

            "updated_at":
                latest_intervention
                .updated_at,
        }

    return response


# ============================================================
# 4. INTERVENTION QUEUE
# ============================================================


@router.get("/interventions")
def intervention_queue(

    status: str | None = Query(
        default="PENDING_REVIEW"
    ),

    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),

    db: Session = Depends(get_db),
):

    query = (
        db.query(
            InterventionTask,
            Student,
            RiskInference,
        )
        .join(
            Student,
            Student.student_id
            == InterventionTask.student_id,
        )
        .join(
            RiskInference,
            RiskInference.inference_id
            == InterventionTask.inference_id,
        )
    )

    if status:

        query = query.filter(
            InterventionTask.status
            == status
        )

    rows = (
        query
        .order_by(
            RiskInference
            .risk_score
            .desc()
        )
        .limit(limit)
        .all()
    )

    interventions = []

    for (
        task,
        student,
        inference,
    ) in rows:

        interventions.append(
            {

                "task_id":
                    str(
                        task.task_id
                    ),

                "student_id":
                    str(
                        student.student_id
                    ),

                "student_code":
                    student.student_code,

                "display_name":
                    student.display_name,

                "risk_score":
                    float(
                        inference.risk_score
                    ),

                "risk_percentage":
                    round(
                        float(
                            inference.risk_score
                        )
                        * 100,
                        2,
                    ),

                "risk_tier":
                    inference.risk_tier,

                "top_risk_factors":
                    inference.top_factors,

                "route":
                    task.routed_domain,

                "plan":
                    task.remediation_plan,

                "outreach_message":
                    task
                    .outreach_message_draft,

                "status":
                    task.status,

                "mentor_notes":
                    task.mentor_notes,

                "updated_at":
                    task.updated_at,
            }
        )

    return {
        "count":
            len(interventions),

        "interventions":
            interventions,
    }


# ============================================================
# 5. RISK HISTORY
# ============================================================


@router.get(
    "/student/{student_code}/risk-history"
)
def student_risk_history(

    student_code: str,

    db: Session = Depends(get_db),
):

    student = (
        db.query(Student)
        .filter(
            Student.student_code
            == student_code
        )
        .first()
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    rows = (
        db.query(
            RiskInference,
            StudentFeatureSnapshot,
        )
        .join(
            StudentFeatureSnapshot,
            RiskInference.snapshot_id
            == StudentFeatureSnapshot
            .snapshot_id,
        )
        .filter(
            RiskInference.student_id
            == student.student_id
        )
        .order_by(
            StudentFeatureSnapshot
            .week_start_date
            .asc()
        )
        .all()
    )

    history = []

    for (
        inference,
        snapshot,
    ) in rows:

        history.append(
            {

                "snapshot_id":
                    str(
                        snapshot.snapshot_id
                    ),

                "week_start_date":
                    snapshot
                    .week_start_date,

                "risk_score":
                    float(
                        inference.risk_score
                    ),

                "risk_percentage":
                    round(
                        float(
                            inference.risk_score
                        )
                        * 100,
                        2,
                    ),

                "risk_tier":
                    inference.risk_tier,

                "top_risk_factors":
                    inference.top_factors,

                "evaluated_at":
                    inference.evaluated_at,
            }
        )

    return {

        "student_code":
            student.student_code,

        "display_name":
            student.display_name,

        "history":
            history,
    }