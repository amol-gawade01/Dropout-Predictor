from sqlalchemy import (
    case,
    func,
)

from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    InterventionTask,
    RiskInference,
    SocraticDialogueLog,
    Student,
    StudentConceptMastery,
    StudentLearningSession,
)


MASTERY_THRESHOLD = 0.80


# ============================================================
# LATEST RISK INFERENCES
# ============================================================


def get_latest_risks(
    db: Session,
):

    """
    PostgreSQL DISTINCT ON behavior through SQLAlchemy.

    Returns only the newest risk inference
    for each student.
    """

    return (
        db.query(RiskInference)
        .order_by(
            RiskInference.student_id.asc(),
            RiskInference.evaluated_at.desc(),
        )
        .distinct(
            RiskInference.student_id
        )
        .all()
    )


# ============================================================
# FACULTY OVERVIEW
# ============================================================


def get_faculty_learning_overview(
    db: Session,
):

    total_students = (
        db.query(
            func.count(
                Student.student_id
            )
        )
        .scalar()
        or 0
    )


    students_with_mastery = (
        db.query(
            func.count(
                func.distinct(
                    StudentConceptMastery
                    .student_id
                )
            )
        )
        .scalar()
        or 0
    )


    avg_mastery = (
        db.query(
            func.avg(
                StudentConceptMastery
                .mastery_prob
            )
        )
        .scalar()
    )

    avg_mastery = (
        float(avg_mastery)
        if avg_mastery is not None
        else 0.0
    )


    students_needing_practice = (
        db.query(
            func.count(
                func.distinct(
                    StudentConceptMastery
                    .student_id
                )
            )
        )
        .filter(
            StudentConceptMastery
            .mastery_prob
            < MASTERY_THRESHOLD
        )
        .scalar()
        or 0
    )


    active_sessions = (
        db.query(
            func.count(
                StudentLearningSession
                .session_id
            )
        )
        .filter(
            StudentLearningSession.status
            == "ACTIVE"
        )
        .scalar()
        or 0
    )


    completed_sessions = (
        db.query(
            func.count(
                StudentLearningSession
                .session_id
            )
        )
        .filter(
            StudentLearningSession.status
            == "COMPLETED"
        )
        .scalar()
        or 0
    )


    dialogue_count = (
        db.query(
            func.count(
                SocraticDialogueLog
                .interaction_id
            )
        )
        .scalar()
        or 0
    )


    latest_risks = (
        get_latest_risks(
            db
        )
    )


    low = 0
    moderate = 0
    critical = 0

    for risk in latest_risks:

        if risk.risk_tier == "LOW":
            low += 1

        elif risk.risk_tier == "MODERATE":
            moderate += 1

        elif risk.risk_tier == "CRITICAL":
            critical += 1


    pending_interventions = (
        db.query(
            func.count(
                InterventionTask.task_id
            )
        )
        .filter(
            InterventionTask.status
            == "PENDING_REVIEW"
        )
        .scalar()
        or 0
    )


    return {

        "students": {
            "total":
                total_students,

            "with_tutor_mastery":
                students_with_mastery,

            "needing_practice":
                students_needing_practice,
        },

        "risk": {
            "evaluated_students":
                len(latest_risks),

            "low":
                low,

            "moderate":
                moderate,

            "critical":
                critical,
        },

        "learning": {
            "average_mastery_percentage":
                round(
                    avg_mastery * 100,
                    2,
                ),

            "active_sessions":
                active_sessions,

            "completed_sessions":
                completed_sessions,

            "total_socratic_interactions":
                dialogue_count,
        },

        "faculty": {
            "pending_interventions":
                pending_interventions,
        },
    }


# ============================================================
# WEAK CONCEPTS
# ============================================================


def get_weak_concept_insights(
    db: Session,
    limit: int = 10,
):

    rows = (
        db.query(

            Concept.concept_id,

            Concept.topic_name,

            func.count(
                StudentConceptMastery.student_id
            ).label(
                "tracked_students"
            ),

            func.avg(
                StudentConceptMastery
                .mastery_prob
            ).label(
                "avg_mastery"
            ),

            func.sum(
                case(
                    (
                        StudentConceptMastery
                        .mastery_prob
                        < MASTERY_THRESHOLD,
                        1,
                    ),
                    else_=0,
                )
            ).label(
                "weak_students"
            ),

            func.avg(
                StudentConceptMastery
                .total_attempts
            ).label(
                "avg_attempts"
            ),
        )

        .join(
            StudentConceptMastery,
            StudentConceptMastery
            .concept_id
            == Concept.concept_id,
        )

        .group_by(
            Concept.concept_id,
            Concept.topic_name,
        )

        .order_by(
            func.avg(
                StudentConceptMastery
                .mastery_prob
            ).asc()
        )

        .limit(limit)

        .all()
    )


    result = []

    for row in rows:

        tracked = (
            int(
                row.tracked_students
            )
            if row.tracked_students
            else 0
        )

        weak = (
            int(
                row.weak_students
            )
            if row.weak_students
            else 0
        )

        weak_percentage = (
            weak / tracked * 100
            if tracked
            else 0
        )

        result.append(
            {
                "concept_id":
                    row.concept_id,

                "topic_name":
                    row.topic_name,

                "tracked_students":
                    tracked,

                "students_below_mastery":
                    weak,

                "weak_student_percentage":
                    round(
                        weak_percentage,
                        2,
                    ),

                "average_mastery_percentage":
                    round(
                        float(
                            row.avg_mastery
                        )
                        * 100,
                        2,
                    ),

                "average_attempts":
                    round(
                        float(
                            row.avg_attempts
                        )
                        if row.avg_attempts
                        is not None
                        else 0,
                        2,
                    ),
            }
        )


    return {
        "count":
            len(result),

        "mastery_threshold_percentage":
            MASTERY_THRESHOLD
            * 100,

        "concepts":
            result,
    }


# ============================================================
# MISCONCEPTION INSIGHTS
# ============================================================


def get_misconception_insights(
    db: Session,
    limit: int = 20,
):

    rows = (
        db.query(

            Concept.concept_id,

            Concept.topic_name,

            SocraticDialogueLog
            .diagnosed_error,

            func.count(
                SocraticDialogueLog
                .interaction_id
            ).label(
                "occurrences"
            ),
        )

        .join(
            Concept,
            Concept.concept_id
            == SocraticDialogueLog
            .concept_id,
        )

        .filter(
            SocraticDialogueLog
            .diagnosed_error
            != "CORRECT"
        )

        .group_by(
            Concept.concept_id,
            Concept.topic_name,
            SocraticDialogueLog
            .diagnosed_error,
        )

        .order_by(
            func.count(
                SocraticDialogueLog
                .interaction_id
            ).desc()
        )

        .limit(limit)

        .all()
    )


    return {

        "count":
            len(rows),

        "misconceptions": [

            {
                "concept_id":
                    row.concept_id,

                "topic_name":
                    row.topic_name,

                "diagnosis":
                    row.diagnosed_error,

                "occurrences":
                    row.occurrences,
            }

            for row
            in rows
        ],
    }


# ============================================================
# AT-RISK STUDENTS
# ============================================================


def get_faculty_at_risk_students(
    db: Session,
    limit: int = 50,
):

    latest_risks = (
        get_latest_risks(
            db
        )
    )


    latest_risks = [
        risk
        for risk in latest_risks
        if risk.risk_tier
        in {
            "MODERATE",
            "CRITICAL",
        }
    ]


    latest_risks.sort(
        key=lambda risk:
            float(
                risk.risk_score
            ),
        reverse=True,
    )


    latest_risks = (
        latest_risks[:limit]
    )


    student_ids = [
        risk.student_id
        for risk in latest_risks
    ]


    students = (
        db.query(Student)
        .filter(
            Student.student_id
            .in_(student_ids)
        )
        .all()
        if student_ids
        else []
    )


    student_map = {
        student.student_id:
            student
        for student in students
    }


    mastery_rows = (
        db.query(

            StudentConceptMastery
            .student_id,

            func.avg(
                StudentConceptMastery
                .mastery_prob
            ).label(
                "avg_mastery"
            ),
        )

        .filter(
            StudentConceptMastery
            .student_id
            .in_(student_ids)
        )

        .group_by(
            StudentConceptMastery
            .student_id
        )

        .all()
        if student_ids
        else []
    )


    mastery_map = {
        row.student_id:
            float(
                row.avg_mastery
            )
        for row in mastery_rows
    }


    result = []


    for risk in latest_risks:

        student = (
            student_map.get(
                risk.student_id
            )
        )

        if student is None:
            continue


        avg_mastery = (
            mastery_map.get(
                student.student_id
            )
        )


        result.append(
            {
                "student_code":
                    student.student_code,

                "display_name":
                    student.display_name,

                "program_stream":
                    student.program_stream,

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

                "top_risk_factors":
                    (
                        risk.top_factors
                        or []
                    )[:3],

                "average_mastery_percentage": (
                    round(
                        avg_mastery
                        * 100,
                        2,
                    )
                    if avg_mastery
                    is not None
                    else None
                ),

                "evaluated_at":
                    risk.evaluated_at,
            }
        )


    return {

        "count":
            len(result),

        "students":
            result,
    }


# ============================================================
# INDIVIDUAL STUDENT LEARNING PROFILE
# ============================================================


def get_faculty_student_profile(
    db: Session,
    student_code: str,
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

        raise ValueError(
            "Student not found"
        )


    latest_risk = (
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


    mastery_rows = (
        db.query(
            StudentConceptMastery,
            Concept,
        )

        .join(
            Concept,
            Concept.concept_id
            == StudentConceptMastery
            .concept_id,
        )

        .filter(
            StudentConceptMastery
            .student_id
            == student.student_id
        )

        .order_by(
            StudentConceptMastery
            .mastery_prob
            .asc()
        )

        .all()
    )


    recent_sessions = (
        db.query(
            StudentLearningSession
        )

        .filter(
            StudentLearningSession.student_id
            == student.student_id
        )

        .order_by(
            StudentLearningSession
            .started_at
            .desc()
        )

        .limit(10)

        .all()
    )


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


    return {

        "student": {
            "student_code":
                student.student_code,

            "display_name":
                student.display_name,

            "program_stream":
                student.program_stream,

            "preferred_language":
                student.preferred_language,
        },

        "risk": (
            {
                "risk_score":
                    float(
                        latest_risk
                        .risk_score
                    ),

                "risk_percentage":
                    round(
                        float(
                            latest_risk
                            .risk_score
                        )
                        * 100,
                        2,
                    ),

                "risk_tier":
                    latest_risk
                    .risk_tier,

                "top_factors":
                    latest_risk
                    .top_factors,

                "evaluated_at":
                    latest_risk
                    .evaluated_at,
            }

            if latest_risk
            else None
        ),

        "mastery": [

            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "mastery_percentage":
                    round(
                        float(
                            mastery
                            .mastery_prob
                        )
                        * 100,
                        2,
                    ),

                "total_attempts":
                    mastery.total_attempts,

                "consecutive_correct":
                    mastery
                    .consecutive_correct,

                "mastered":
                    mastery
                    .mastery_prob
                    >= MASTERY_THRESHOLD,
            }

            for mastery, concept
            in mastery_rows
        ],

        "recent_sessions": [

            {
                "session_id":
                    str(
                        session.session_id
                    ),

                "primary_concept_id":
                    session
                    .primary_concept_id,

                "status":
                    session.status,

                "answered_questions":
                    session
                    .answered_questions,

                "correct_answers":
                    session
                    .correct_answers,

                "started_at":
                    session.started_at,

                "ended_at":
                    session.ended_at,
            }

            for session
            in recent_sessions
        ],

        "latest_intervention": (
            {
                "task_id":
                    str(
                        latest_intervention
                        .task_id
                    ),

                "route":
                    latest_intervention
                    .routed_domain,

                "status":
                    latest_intervention
                    .status,

                "plan":
                    latest_intervention
                    .remediation_plan,

                "mentor_notes":
                    latest_intervention
                    .mentor_notes,
            }

            if latest_intervention
            else None
        ),
    }