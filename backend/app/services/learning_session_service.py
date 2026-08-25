from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    Student,
    StudentConceptMastery,
    StudentLearningSession,
    StudentLearningSessionAttempt,
)

from backend.app.services.adaptive_tutor_service import (
    process_adaptive_attempt,
)

from tutor.question_selector import (
    select_question,
)
from tutor.question_bank import get_display_question, get_questions_for_concept


# ============================================================
# STUDENT
# ============================================================


def find_student(
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
# MASTERY
# ============================================================


def get_mastery_probability(
    db: Session,
    student_id,
    concept_id: str,
) -> float:

    mastery = (
        db.query(
            StudentConceptMastery
        )
        .filter(
            StudentConceptMastery.student_id
            == student_id,

            StudentConceptMastery.concept_id
            == concept_id,
        )
        .first()
    )

    if mastery is None:
        return 0.20

    return float(
        mastery.mastery_prob
    )


# ============================================================
# GET SESSION
# ============================================================


def get_learning_session(
    db: Session,
    session_id: UUID,
):

    session = db.get(
        StudentLearningSession,
        session_id,
    )

    if session is None:
        raise ValueError(
            "Learning session not found"
        )

    return session


# ============================================================
# USED QUESTIONS
# ============================================================


def get_used_question_ids(
    db: Session,
    session_id,
):

    rows = (
        db.query(
            StudentLearningSessionAttempt.question_id
        )
        .filter(
            StudentLearningSessionAttempt.session_id
            == session_id
        )
        .all()
    )

    return {
        row[0]
        for row in rows
    }


# ============================================================
# NEXT QUESTION
# ============================================================


def get_next_session_question(
    db: Session,
    session: StudentLearningSession,
):

    if session.status != "ACTIVE":

        return {
            "session_complete": True,
            "reason":
                session.completion_reason
                or "SESSION_NOT_ACTIVE",
            "question": None,
        }


    # Target reached.
    if (
        session.answered_questions
        >= session.target_questions
    ):

        complete_learning_session(
            db=db,
            session=session,
            reason="TARGET_REACHED",
        )

        return {
            "session_complete": True,
            "reason": "TARGET_REACHED",
            "question": None,
        }


    mastery_prob = (
        get_mastery_probability(
            db=db,
            student_id=
                session.student_id,
            concept_id=
                session.active_concept_id,
        )
    )


    used_question_ids = (
        get_used_question_ids(
            db,
            session.session_id,
        )
    )


    question = select_question(

        concept_id=
            session.active_concept_id,

        mastery_prob=
            mastery_prob,

        exclude_question_ids=
            used_question_ids,
    )


    # We have no unused question left
    # for the current concept.
    if question is None:

        complete_learning_session(
            db=db,
            session=session,
            reason="QUESTION_BANK_EXHAUSTED",
        )

        return {
            "session_complete": True,

            "reason":
                "QUESTION_BANK_EXHAUSTED",

            "question": None,
        }


    concept = db.get(
        Concept,
        session.active_concept_id,
    )


    return {

        "session_complete":
            False,

        "reason":
            None,

        "active_concept": {

            "concept_id":
                concept.concept_id,

            "topic_name":
                concept.topic_name,
        },

        "current_mastery":
            mastery_prob,

        "question": {

            "question_id":
                question[
                    "question_id"
                ],

            "text":
                get_display_question(
                    question,
                    session.language_code,
                ),

            "difficulty":
                question[
                    "difficulty"
                ],
        },
    }


# ============================================================
# START SESSION
# ============================================================


def start_learning_session(
    db: Session,
    student_code: str,
    concept_id: str,
    target_questions: int,
    language_code: str,
):

    student = find_student(
        db,
        student_code,
    )

    concept = db.get(
        Concept,
        concept_id,
    )

    if concept is None:
        raise ValueError(
            "Concept not found"
        )

    if not get_questions_for_concept(concept.concept_id):
        raise ValueError(
            "This concept does not have practice questions yet"
        )


    starting_mastery = (
        get_mastery_probability(
            db=db,
            student_id=
                student.student_id,
            concept_id=
                concept.concept_id,
        )
    )


    session = StudentLearningSession(

        student_id=
            student.student_id,

        primary_concept_id=
            concept.concept_id,

        active_concept_id=
            concept.concept_id,

        language_code=
            language_code,

        target_questions=
            target_questions,

        answered_questions=
            0,

        correct_answers=
            0,

        starting_mastery=
            starting_mastery,

        status=
            "ACTIVE",
    )


    db.add(session)

    db.commit()

    db.refresh(session)


    next_question = (
        get_next_session_question(
            db,
            session,
        )
    )


    return {

        "session_id":
            str(
                session.session_id
            ),

        "status":
            session.status,

        "student_code":
            student.student_code,

        "concept": {

            "concept_id":
                concept.concept_id,

            "topic_name":
                concept.topic_name,
        },

        "target_questions":
            session.target_questions,

        "starting_mastery":
            starting_mastery,

        "next":
            next_question,
    }


# ============================================================
# COMPLETE SESSION
# ============================================================


def complete_learning_session(
    db: Session,
    session: StudentLearningSession,
    reason: str,
):

    if session.status != "ACTIVE":
        return session


    final_mastery = (
        get_mastery_probability(
            db=db,
            student_id=
                session.student_id,
            concept_id=
                session.primary_concept_id,
        )
    )


    session.final_mastery = (
        final_mastery
    )

    session.status = (
        "COMPLETED"
    )

    session.completion_reason = (
        reason
    )

    session.ended_at = (
        datetime.now(
            timezone.utc
        )
    )


    db.commit()

    db.refresh(session)

    return session


# ============================================================
# SUBMIT SESSION ANSWER
# ============================================================


def answer_learning_session(
    db: Session,
    session_id: UUID,
    question_id: str,
    student_answer: str,
):

    session = get_learning_session(
        db,
        session_id,
    )


    if session.status != "ACTIVE":

        raise ValueError(
            "Learning session is not active"
        )


    student = db.get(
        Student,
        session.student_id,
    )


    # Prevent answering the same question
    # twice in one session.
    existing_attempt = (
        db.query(
            StudentLearningSessionAttempt
        )
        .filter(
            StudentLearningSessionAttempt.session_id
            == session.session_id,

            StudentLearningSessionAttempt.question_id
            == question_id,
        )
        .first()
    )

    if existing_attempt:

        raise ValueError(
            "Question already answered "
            "in this session"
        )


    # ========================================================
    # USE EXISTING ADAPTIVE TUTOR PIPELINE
    # ========================================================

    tutor_result = (
        process_adaptive_attempt(

            db=db,

            student_code=
                student.student_code,

            question_id=
                question_id,

            student_answer=
                student_answer,

            language_code=
                session.language_code,
        )
    )


    # ========================================================
    # SAVE SESSION ATTEMPT
    # ========================================================

    interaction_id = (
        tutor_result.get(
            "interaction_id"
        )
    )


    attempt = (
        StudentLearningSessionAttempt(

            session_id=
                session.session_id,

            interaction_id=(
                UUID(interaction_id)
                if interaction_id
                else None
            ),

            question_id=
                question_id,

            concept_id=
                tutor_result[
                    "question"
                ][
                    "concept_id"
                ],

            is_correct=
                tutor_result[
                    "evaluation"
                ][
                    "is_correct"
                ],

            diagnosis=
                tutor_result[
                    "evaluation"
                ][
                    "diagnosis"
                ],

            mastery_before=
                tutor_result[
                    "mastery"
                ][
                    "before"
                ],

            mastery_after=
                tutor_result[
                    "mastery"
                ][
                    "after"
                ],
        )
    )


    db.add(attempt)


    session.answered_questions += 1


    if tutor_result[
        "evaluation"
    ][
        "is_correct"
    ]:

        session.correct_answers += 1


    # ========================================================
    # PREREQUISITE REDIRECTION
    # ========================================================

    recommended_concept = (
        tutor_result.get(
            "recommended_concept"
        )
    )


    if recommended_concept:

        session.active_concept_id = (
            recommended_concept[
                "concept_id"
            ]
        )


    db.commit()

    db.refresh(session)

    db.refresh(attempt)


    # ========================================================
    # CHECK SESSION COMPLETION
    # ========================================================

    if (
        session.answered_questions
        >= session.target_questions
    ):

        complete_learning_session(
            db=db,
            session=session,
            reason="TARGET_REACHED",
        )

        next_data = {

            "session_complete":
                True,

            "reason":
                "TARGET_REACHED",

            "question":
                None,
        }

    else:

        next_data = (
            get_next_session_question(
                db,
                session,
            )
        )


    return {

        "session_id":
            str(
                session.session_id
            ),

        "attempt_number":
            session.answered_questions,

        "attempt":
            tutor_result,

        "progress": {

            "answered":
                session
                .answered_questions,

            "target":
                session
                .target_questions,

            "correct":
                session
                .correct_answers,

            "accuracy_percentage":
                round(
                    (
                        session
                        .correct_answers
                        /
                        session
                        .answered_questions
                        * 100
                    )
                    if session
                    .answered_questions
                    else 0,
                    2,
                ),
        },

        "next":
            next_data,
    }


# ============================================================
# SESSION SUMMARY
# ============================================================


def get_learning_session_summary(
    db: Session,
    session_id: UUID,
):

    session = get_learning_session(
        db,
        session_id,
    )


    student = db.get(
        Student,
        session.student_id,
    )


    primary_concept = db.get(
        Concept,
        session.primary_concept_id,
    )


    active_concept = db.get(
        Concept,
        session.active_concept_id,
    )


    attempts = (
        db.query(
            StudentLearningSessionAttempt
        )
        .filter(
            StudentLearningSessionAttempt.session_id
            == session.session_id
        )
        .order_by(
            StudentLearningSessionAttempt
            .created_at
            .asc()
        )
        .all()
    )


    current_mastery = (
        get_mastery_probability(
            db=db,
            student_id=
                session.student_id,
            concept_id=
                session
                .primary_concept_id,
        )
    )


    accuracy = (
        round(
            (
                session.correct_answers
                /
                session.answered_questions
                * 100
            )
            if session.answered_questions
            else 0,
            2,
        )
    )


    diagnosis_counts = {}

    for attempt in attempts:

        diagnosis_counts[
            attempt.diagnosis
        ] = (
            diagnosis_counts.get(
                attempt.diagnosis,
                0,
            )
            + 1
        )


    return {

        "session_id":
            str(
                session.session_id
            ),

        "status":
            session.status,

        "completion_reason":
            session
            .completion_reason,

        "student_code":
            student.student_code,

        "primary_concept": {

            "concept_id":
                primary_concept
                .concept_id,

            "topic_name":
                primary_concept
                .topic_name,
        },

        "active_concept": {

            "concept_id":
                active_concept
                .concept_id,

            "topic_name":
                active_concept
                .topic_name,
        },

        "progress": {

            "target_questions":
                session
                .target_questions,

            "answered_questions":
                session
                .answered_questions,

            "correct_answers":
                session
                .correct_answers,

            "accuracy_percentage":
                accuracy,
        },

        "mastery": {

            "starting":
                float(
                    session
                    .starting_mastery
                ),

            "current":
                current_mastery,

            "change":
                round(
                    current_mastery
                    - float(
                        session
                        .starting_mastery
                    ),
                    4,
                ),
        },

        "diagnoses":
            diagnosis_counts,

        "attempts": [

            {
                "attempt_id":
                    str(
                        attempt
                        .attempt_id
                    ),

                "question_id":
                    attempt
                    .question_id,

                "concept_id":
                    attempt
                    .concept_id,

                "is_correct":
                    attempt
                    .is_correct,

                "diagnosis":
                    attempt
                    .diagnosis,

                "mastery_before":
                    attempt
                    .mastery_before,

                "mastery_after":
                    attempt
                    .mastery_after,

                "created_at":
                    attempt
                    .created_at,
            }

            for attempt
            in attempts
        ],

        "started_at":
            session.started_at,

        "ended_at":
            session.ended_at,
    }

def get_student_learning_sessions(
    db: Session,
    student_code: str,
    limit: int = 20,
):

    student = find_student(
        db,
        student_code,
    )

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
        .limit(limit)
        .all()
    )

    result = []

    for session in sessions:

        concept = db.get(
            Concept,
            session.primary_concept_id,
        )

        accuracy = (
            (
                session.correct_answers
                /
                session.answered_questions
                * 100
            )
            if session.answered_questions
            else 0
        )

        result.append(
            {
                "session_id":
                    str(
                        session.session_id
                    ),

                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "status":
                    session.status,

                "answered_questions":
                    session
                    .answered_questions,

                "correct_answers":
                    session
                    .correct_answers,

                "accuracy_percentage":
                    round(
                        accuracy,
                        2,
                    ),

                "starting_mastery":
                    float(
                        session
                        .starting_mastery
                    ),

                "final_mastery": (
                    float(
                        session
                        .final_mastery
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
        )

    return {

        "student_code":
            student.student_code,

        "count":
            len(result),

        "sessions":
            result,
    }