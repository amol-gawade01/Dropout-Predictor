from sqlalchemy import (
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
    StudentFeatureSnapshot,
    StudentLearningSession,
    StudentLearningSessionAttempt,
)


MASTERY_THRESHOLD = 0.80


# ============================================================
# STUDENT
# ============================================================


def get_student(
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

    return student


# ============================================================
# ACADEMIC SNAPSHOT
# ============================================================


def get_student_academic_summary(
    db: Session,
    student_code: str,
):
    """Return the latest institution-provided academic snapshot."""
    student = get_student(db, student_code)
    snapshot = (
        db.query(StudentFeatureSnapshot)
        .filter(StudentFeatureSnapshot.student_id == student.student_id)
        .order_by(StudentFeatureSnapshot.week_start_date.desc())
        .first()
    )

    if snapshot is None:
        return {
            "available": False,
            "message": "No attendance or academic result has been uploaded yet.",
        }

    return {
        "available": True,
        "semester": snapshot.semester,
        "week_start_date": snapshot.week_start_date,
        "current_gpa": round(float(snapshot.current_gpa), 2),
        "failed_subjects": snapshot.failed_subjects,
        "backlog_count": snapshot.backlog_count,
        "credits_completion_percentage": round(float(snapshot.credits_completion_ratio) * 100, 2),
        "attendance_percentage": round(float(snapshot.attendance_pct), 2),
        "attendance_change_14d": round(float(snapshot.attendance_velocity_14d), 2),
        "consecutive_absent_days": snapshot.consecutive_absent_days,
        "assignment_completion_percentage": round(float(snapshot.assignment_completion_pct), 2),
        "missed_assessments": snapshot.missed_assessments,
        "source": snapshot.source,
    }


# ============================================================
# SUPPORT LEVEL
# ============================================================


def support_level_from_risk(
    risk_tier: str | None,
):

    if risk_tier == "CRITICAL":
        return "HIGH_SUPPORT"

    if risk_tier == "MODERATE":
        return "EXTRA_SUPPORT"

    if risk_tier == "LOW":
        return "ON_TRACK"

    return "NOT_EVALUATED"


# ============================================================
# CONCEPT PROGRESS
# ============================================================


def get_student_concept_progress(
    db: Session,
    student,
):

    concepts = (
        db.query(Concept)
        .order_by(
            Concept.topic_name.asc()
        )
        .all()
    )


    mastery_rows = (
        db.query(
            StudentConceptMastery
        )

        .filter(
            StudentConceptMastery.student_id
            == student.student_id
        )

        .all()
    )


    mastery_map = {
        row.concept_id:
            row
        for row in mastery_rows
    }


    progress = []


    for concept in concepts:

        mastery = (
            mastery_map.get(
                concept.concept_id
            )
        )


        if mastery:

            mastery_prob = float(
                mastery.mastery_prob
            )

            attempts = (
                mastery.total_attempts
            )

            consecutive = (
                mastery
                .consecutive_correct
            )

        else:

            mastery_prob = 0.20
            attempts = 0
            consecutive = 0


        progress.append(
            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "prerequisite_concept_id":
                    concept
                    .prerequisite_concept_id,

                "mastery_probability":
                    mastery_prob,

                "mastery_percentage":
                    round(
                        mastery_prob
                        * 100,
                        2,
                    ),

                "mastered":
                    mastery_prob
                    >= MASTERY_THRESHOLD,

                "total_attempts":
                    attempts,

                "consecutive_correct":
                    consecutive,
            }
        )


    return progress


# ============================================================
# RECOMMEND NEXT CONCEPTS
# ============================================================


def build_learning_recommendations(
    progress: list,
    limit: int = 3,
):

    # First prioritize weak concepts
    # the student has already attempted.

    attempted_weak = [
        item
        for item in progress
        if (
            not item[
                "mastered"
            ]
            and
            item[
                "total_attempts"
            ] > 0
        )
    ]


    attempted_weak.sort(
        key=lambda item:
            item[
                "mastery_probability"
            ]
    )


    if attempted_weak:

        selected = (
            attempted_weak[:limit]
        )

    else:

        # If the student hasn't practiced
        # anything yet, suggest foundational
        # concepts first.

        foundations = [
            item
            for item in progress
            if (
                item[
                    "prerequisite_concept_id"
                ]
                is None
            )
        ]

        selected = (
            foundations[:limit]
        )


    return [

        {
            "concept_id":
                item[
                    "concept_id"
                ],

            "topic_name":
                item[
                    "topic_name"
                ],

            "mastery_percentage":
                item[
                    "mastery_percentage"
                ],

            "reason": (
                "LOW_MASTERY"
                if item[
                    "total_attempts"
                ] > 0
                else "FOUNDATIONAL_CONCEPT"
            ),

            "next_question_endpoint": (
                "/api/v1/tutor/"
                "next-question/"
                "{student_code}/"
                f"{item['concept_id']}"
            ),
        }

        for item in selected
    ]


# ============================================================
# STUDENT DASHBOARD
# ============================================================


def build_student_dashboard(
    db: Session,
    student_code: str,
):

    student = get_student(
        db,
        student_code,
    )


    # ========================================================
    # LATEST RISK
    # ========================================================

    risk = (
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


    # ========================================================
    # MASTERY
    # ========================================================

    progress = (
        get_student_concept_progress(
            db,
            student,
        )
    )


    tracked = [
        item
        for item in progress
        if item[
            "total_attempts"
        ] > 0
    ]


    mastered_count = sum(
        1
        for item in tracked
        if item["mastered"]
    )


    needs_practice_count = sum(
        1
        for item in tracked
        if not item["mastered"]
    )


    if tracked:

        average_mastery = (
            sum(
                item[
                    "mastery_probability"
                ]
                for item in tracked
            )
            / len(tracked)
        )

    else:

        average_mastery = 0.20


    # ========================================================
    # SESSIONS
    # ========================================================

    sessions = (
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

        .limit(5)

        .all()
    )


    total_sessions = (
        db.query(
            func.count(
                StudentLearningSession
                .session_id
            )
        )

        .filter(
            StudentLearningSession.student_id
            == student.student_id
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
            StudentLearningSession.student_id
            == student.student_id,

            StudentLearningSession.status
            == "COMPLETED",
        )

        .scalar()
        or 0
    )


    # ========================================================
    # RECENT TUTOR INTERACTIONS
    # ========================================================

    dialogues = (
        db.query(
            SocraticDialogueLog,
            Concept,
        )

        .join(
            Concept,
            Concept.concept_id
            == SocraticDialogueLog
            .concept_id,
        )

        .filter(
            SocraticDialogueLog.student_id
            == student.student_id
        )

        .order_by(
            SocraticDialogueLog
            .created_at
            .desc()
        )

        .limit(5)

        .all()
    )


    # ========================================================
    # INTERVENTION STATUS
    # ========================================================

    intervention = (
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


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    recommendations = (
        build_learning_recommendations(
            progress,
            limit=3,
        )
    )


    # Replace endpoint placeholder
    for item in recommendations:

        item[
            "next_question_endpoint"
        ] = (
            item[
                "next_question_endpoint"
            ]
            .replace(
                "{student_code}",
                student.student_code,
            )
        )


    # ========================================================
    # RESPONSE
    # ========================================================

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

        "academic_summary":
            get_student_academic_summary(
                db=db,
                student_code=student.student_code,
            ),

        "support": {
            "level":
                support_level_from_risk(
                    risk.risk_tier
                    if risk
                    else None
                ),

            # Useful for demo/admin.
            # On the real student UI you can
            # choose not to show raw dropout score.
            "risk_tier": (
                risk.risk_tier
                if risk
                else None
            ),

            "top_learning_risk_factors": (
                (
                    risk.top_factors
                    or []
                )[:3]
                if risk
                else []
            ),

            "faculty_support_status": (
                intervention.status
                if intervention
                else None
            ),
        },

        "learning_summary": {

            "average_mastery_percentage":
                round(
                    average_mastery
                    * 100,
                    2,
                ),

            "tracked_concepts":
                len(tracked),

            "mastered_concepts":
                mastered_count,

            "concepts_needing_practice":
                needs_practice_count,

            "total_sessions":
                total_sessions,

            "completed_sessions":
                completed_sessions,
        },

        "recommended_next":
            recommendations,

        "recent_sessions": [

            {
                "session_id":
                    str(
                        session.session_id
                    ),

                "concept_id":
                    session
                    .primary_concept_id,

                "status":
                    session.status,

                "answered":
                    session
                    .answered_questions,

                "target":
                    session
                    .target_questions,

                "correct":
                    session
                    .correct_answers,

                "starting_mastery_percentage":
                    round(
                        float(
                            session
                            .starting_mastery
                        )
                        * 100,
                        2,
                    ),

                "final_mastery_percentage": (
                    round(
                        float(
                            session
                            .final_mastery
                        )
                        * 100,
                        2,
                    )
                    if session
                    .final_mastery
                    is not None
                    else None
                ),

                "started_at":
                    session.started_at,

                "ended_at":
                    session.ended_at,
            }

            for session
            in sessions
        ],

        "recent_tutor_activity": [

            {
                "interaction_id":
                    str(
                        log.interaction_id
                    ),

                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "diagnosis":
                    log.diagnosed_error,

                "mastery_before_percentage":
                    round(
                        float(
                            log.mastery_prior
                        )
                        * 100,
                        2,
                    ),

                "mastery_after_percentage":
                    round(
                        float(
                            log.mastery_post
                        )
                        * 100,
                        2,
                    ),

                "created_at":
                    log.created_at,
            }

            for log, concept
            in dialogues
        ],
    }


# ============================================================
# MASTERY DETAIL
# ============================================================


def get_student_mastery_dashboard(
    db: Session,
    student_code: str,
):

    student = get_student(
        db,
        student_code,
    )

    progress = (
        get_student_concept_progress(
            db,
            student,
        )
    )


    return {

        "student_code":
            student.student_code,

        "mastery_threshold_percentage":
            MASTERY_THRESHOLD
            * 100,

        "concepts":
            progress,
    }


# ============================================================
# MASTERY TREND
# ============================================================


def get_student_mastery_trend(
    db: Session,
    student_code: str,
    concept_id: str | None = None,
):

    student = get_student(
        db,
        student_code,
    )


    query = (
        db.query(
            StudentLearningSessionAttempt
        )

        .join(
            StudentLearningSession,
            StudentLearningSession
            .session_id
            == StudentLearningSessionAttempt
            .session_id,
        )

        .filter(
            StudentLearningSession.student_id
            == student.student_id
        )
    )


    if concept_id:

        query = query.filter(
            StudentLearningSessionAttempt
            .concept_id
            == concept_id
        )


    attempts = (
        query
        .order_by(
            StudentLearningSessionAttempt
            .created_at
            .asc()
        )
        .all()
    )


    return {

        "student_code":
            student.student_code,

        "concept_id":
            concept_id,

        "points": [

            {
                "question_id":
                    attempt.question_id,

                "concept_id":
                    attempt.concept_id,

                "mastery_before_percentage":
                    round(
                        float(
                            attempt
                            .mastery_before
                        )
                        * 100,
                        2,
                    ),

                "mastery_after_percentage":
                    round(
                        float(
                            attempt
                            .mastery_after
                        )
                        * 100,
                        2,
                    ),

                "is_correct":
                    attempt.is_correct,

                "diagnosis":
                    attempt.diagnosis,

                "created_at":
                    attempt.created_at,
            }

            for attempt
            in attempts
        ],
    }


# ============================================================
# RECENT LEARNING ACTIVITY
# ============================================================


def get_student_recent_activity(
    db: Session,
    student_code: str,
    limit: int = 20,
):

    student = get_student(
        db,
        student_code,
    )


    attempts = (
        db.query(
            StudentLearningSessionAttempt
        )

        .join(
            StudentLearningSession,
            StudentLearningSession
            .session_id
            == StudentLearningSessionAttempt
            .session_id,
        )

        .filter(
            StudentLearningSession.student_id
            == student.student_id
        )

        .order_by(
            StudentLearningSessionAttempt
            .created_at
            .desc()
        )

        .limit(limit)

        .all()
    )


    return {

        "student_code":
            student.student_code,

        "count":
            len(attempts),

        "activity": [

            {
                "attempt_id":
                    str(
                        attempt.attempt_id
                    ),

                "question_id":
                    attempt.question_id,

                "concept_id":
                    attempt.concept_id,

                "is_correct":
                    attempt.is_correct,

                "diagnosis":
                    attempt.diagnosis,

                "mastery_before_percentage":
                    round(
                        float(
                            attempt
                            .mastery_before
                        )
                        * 100,
                        2,
                    ),

                "mastery_after_percentage":
                    round(
                        float(
                            attempt
                            .mastery_after
                        )
                        * 100,
                        2,
                    ),

                "created_at":
                    attempt.created_at,
            }

            for attempt
            in attempts
        ],
    }