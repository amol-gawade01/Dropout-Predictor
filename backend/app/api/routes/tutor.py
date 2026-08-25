from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from backend.app.core.auth import (
    ensure_learning_session_access,
    ensure_student_code_access,
    get_current_student,
    require_roles,
)

from backend.app.db.models import (
    Concept,
    SocraticDialogueLog,
    Student,
    StudentConceptMastery,
    UserAccount,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.schemas.tutor import (
    TutorAttemptRequest,
)

from backend.app.services.tutor_service import (
    process_tutor_attempt,
)


from tutor.question_selector import (
    select_question,
)
from tutor.question_bank import get_display_question

from backend.app.schemas.tutor import (
    AdaptiveTutorAttemptRequest,
    TutorAttemptRequest,
)

from backend.app.services.adaptive_tutor_service import (
    process_adaptive_attempt,
)

from backend.app.services.recommendation_service import (
    build_student_recommendations,
)


from uuid import UUID

from backend.app.schemas.tutor import (
    AdaptiveTutorAttemptRequest,
    EndLearningSessionRequest,
    LearningSessionAnswerRequest,
    StartLearningSessionRequest,
    TutorAttemptRequest,
)

from backend.app.services.learning_session_service import (
    answer_learning_session,
    complete_learning_session,
    get_learning_session,
    get_learning_session_summary,
    get_next_session_question,
    get_student_learning_sessions,
    start_learning_session,
)

router = APIRouter(
    prefix="/tutor",
    tags=["Tutor"],
)


# ============================================================
# 1. LIST CONCEPTS
# ============================================================


@router.get(
    "/me/mastery"
)
def my_tutor_mastery(

    student: Student = Depends(
        get_current_student
    ),

    db: Session = Depends(
        get_db
    ),
):

    # Reuse your mastery logic.
    return mastery_map(
        student_code=
            student.student_code,

        current_user=None,
        db=db,
    )

@router.get("/concepts")
def list_concepts(
    db: Session = Depends(get_db),
):

    concepts = (
        db.query(Concept)
        .order_by(
            Concept.topic_name.asc()
        )
        .all()
    )

    return {

        "count":
            len(concepts),

        "concepts": [

            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "description":
                    concept
                    .concept_description,

                "prerequisite_concept_id":
                    concept
                    .prerequisite_concept_id,
            }

            for concept
            in concepts
        ],
    }


# ============================================================
# 2. STUDENT MASTERY MAP
# ============================================================


@router.get(
    "/mastery/{student_code}"
)
def mastery_map(

    student_code: str,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):
    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            student_code,

        db=db,
    )
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

    mastery_by_concept = {

        row.concept_id:
            row

        for row
        in mastery_rows
    }

    result = []

    for concept in concepts:

        row = mastery_by_concept.get(
            concept.concept_id
        )

        if row:

            mastery_prob = float(
                row.mastery_prob
            )

            attempts = (
                row.total_attempts
            )

            consecutive = (
                row.consecutive_correct
            )

        else:

            mastery_prob = 0.20
            attempts = 0
            consecutive = 0

        result.append(
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
                    >= 0.80,

                "total_attempts":
                    attempts,

                "consecutive_correct":
                    consecutive,
            }
        )

    return {

        "student_code":
            student.student_code,

        "concepts":
            result,
    }


# ============================================================
# 3. PROCESS TUTOR ATTEMPT
# ============================================================


@router.post("/attempt")
def submit_tutor_attempt(

    payload: TutorAttemptRequest,

    db: Session = Depends(get_db),
):

    try:

        return process_tutor_attempt(

            db=db,

            student_code=
                payload.student_code,

            concept_id=
                payload.concept_id,

            question=
                payload.question,

            student_answer=
                payload.student_answer,

            is_correct=
                payload.is_correct,

            language_code=
                payload.language_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    


@router.get(
    "/next-question/"
    "{student_code}/"
    "{concept_id}"
)
def next_question(

    student_code: str,

    concept_id: str,

    language_code: str = Query(
        default="en-IN"
    ),

    current_user:
    UserAccount
    = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(
        get_db
    ),
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


    concept = db.get(
        Concept,
        concept_id,
    )

    if concept is None:

        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )


    mastery = (
        db.query(
            StudentConceptMastery
        )
        .filter(
            StudentConceptMastery.student_id
            == student.student_id,

            StudentConceptMastery.concept_id
            == concept.concept_id,
        )
        .first()
    )


    mastery_prob = (
        float(
            mastery.mastery_prob
        )
        if mastery
        else 0.20
    )


    question = select_question(
        concept_id=
            concept.concept_id,

        mastery_prob=
            mastery_prob,
    )


    if question is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "No questions available "
                "for this concept"
            ),
        )


    # IMPORTANT:
    # Do NOT return expected_answer.

    return {

        "student_code":
            student.student_code,

        "concept_id":
            concept.concept_id,

        "topic_name":
            concept.topic_name,

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
                    language_code,
                ),

            "difficulty":
                question[
                    "difficulty"
                ],
        },
    }
@router.post(
    "/adaptive-attempt"
)
def adaptive_attempt(

    payload:
        AdaptiveTutorAttemptRequest,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT"
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            payload.student_code,

        db=db,
    )


    try:

        return process_adaptive_attempt(

            db=db,

            student_code=
                payload.student_code,

            question_id=
                payload.question_id,

            student_answer=
                payload.student_answer,

            language_code=
                payload.language_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    
# ============================================================
# TUTOR HISTORY
# ============================================================


@router.get(
    "/history/{student_code}"
)
def tutor_history(

    student_code: str,

    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            student_code,

        db=db,
    )

    # ========================================================
    # FIND STUDENT
    # ========================================================

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


    # ========================================================
    # GET DIALOGUE HISTORY
    # ========================================================

    rows = (
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
        .limit(limit)
        .all()
    )


    interactions = []

    for log, concept in rows:

        interactions.append(
            {

                "interaction_id":
                    str(
                        log.interaction_id
                    ),

                "concept": {

                    "concept_id":
                        concept.concept_id,

                    "topic_name":
                        concept.topic_name,
                },

                "student_input":
                    log.student_raw_input,

                "diagnosis":
                    log.diagnosed_error,

                "socratic_response":
                    log
                    .socratic_prompt_returned,

                "mastery_before":
                    float(
                        log.mastery_prior
                    ),

                "mastery_after":
                    float(
                        log.mastery_post
                    ),

                "language_code":
                    log.language_code,

                "created_at":
                    log.created_at,
            }
        )


    return {

        "student_code":
            student.student_code,

        "count":
            len(interactions),

        "interactions":
            interactions,
    }
# ============================================================
# TUTOR HISTORY
# ============================================================


@router.get(
    "/history/{student_code}/{concept_id}"
)
def tutor_concept_history(

    student_code: str,
    concept_id: str,

    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            student_code,

        db=db,
    )

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


    concept = db.get(
        Concept,
        concept_id,
    )

    if concept is None:

        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )


    logs = (
        db.query(
            SocraticDialogueLog
        )
        .filter(
            SocraticDialogueLog.student_id
            == student.student_id,

            SocraticDialogueLog.concept_id
            == concept.concept_id,
        )
        .order_by(
            SocraticDialogueLog
            .created_at
            .desc()
        )
        .limit(limit)
        .all()
    )


    return {

        "student_code":
            student.student_code,

        "concept": {

            "concept_id":
                concept.concept_id,

            "topic_name":
                concept.topic_name,
        },

        "count":
            len(logs),

        "interactions": [

            {
                "interaction_id":
                    str(
                        log.interaction_id
                    ),

                "student_input":
                    log.student_raw_input,

                "diagnosis":
                    log.diagnosed_error,

                "socratic_response":
                    log
                    .socratic_prompt_returned,

                "mastery_before":
                    float(
                        log.mastery_prior
                    ),

                "mastery_after":
                    float(
                        log.mastery_post
                    ),

                "language_code":
                    log.language_code,

                "created_at":
                    log.created_at,
            }

            for log in logs
        ],
    }    

@router.get(
    "/recommendations/{student_code}"
)
def tutor_recommendations(

    student_code: str,

    limit: int = Query(
        default=3,
        ge=1,
        le=10,
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(get_db),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            student_code,

        db=db,
    )

    try:

        result = (
            build_student_recommendations(
                db=db,
                student_code=
                    student_code,
                limit=
                    limit,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


    student = result[
        "student"
    ]

    risk = result[
        "risk"
    ]


    risk_data = None

    if risk:

        risk_data = {

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

            "academic_risk_factors":
                result[
                    "academic_risk_factors"
                ],
        }


    return {

        "student_code":
            student.student_code,

        "display_name":
            student.display_name,

        "ews":
            risk_data,

        "recommendation_count":
            len(
                result[
                    "recommendations"
                ]
            ),

        "recommendations":
            result[
                "recommendations"
            ],
    }  
# ============================================================
# START LEARNING SESSION
# ============================================================

@router.post(
    "/sessions/start"
)
def start_session(

    payload:
        StartLearningSessionRequest,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT"
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            payload.student_code,

        db=db,
    )


    try:

        return start_learning_session(

            db=db,

            student_code=
                payload.student_code,

            concept_id=
                payload.concept_id,

            target_questions=
                payload.target_questions,

            language_code=
                payload.language_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
 
# SESSION DETAILS / SUMMARY
# ============================================================

@router.get(
    "/sessions/{session_id}"
)
def learning_session_details(

    session_id: UUID,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    try:

        learning_session = (
            get_learning_session(
                db,
                session_id,
            )
        )

        ensure_learning_session_access(
            current_user=
                current_user,

            learning_session=
                learning_session,
        )


        return (
            get_learning_session_summary(
                db=db,
                session_id=
                    session_id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
# ============================================================
# SESSION NEXT QUESTION
# ============================================================

@router.get(
    "/sessions/{session_id}/next-question"
)
def session_next_question(

    session_id: UUID,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT"
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    try:

        learning_session = (
            get_learning_session(
                db,
                session_id,
            )
        )


        ensure_learning_session_access(
            current_user=
                current_user,

            learning_session=
                learning_session,
        )


        return (
            get_next_session_question(
                db,
                learning_session,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

# ============================================================
# ANSWER INSIDE LEARNING SESSION
# ============================================================

@router.post(
    "/sessions/{session_id}/answer"
)
def session_answer(

    session_id: UUID,

    payload:
        LearningSessionAnswerRequest,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT"
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    try:

        learning_session = (
            get_learning_session(
                db,
                session_id,
            )
        )


        ensure_learning_session_access(
            current_user=
                current_user,

            learning_session=
                learning_session,
        )


        return (
            answer_learning_session(

                db=db,

                session_id=
                    session_id,

                question_id=
                    payload.question_id,

                student_answer=
                    payload.student_answer,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
# ============================================================
# END SESSION
# ============================================================


@router.post(
    "/sessions/{session_id}/end"
)
def end_session(

    session_id: UUID,

    payload:
        EndLearningSessionRequest,

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT"
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    try:

        learning_session = (
            get_learning_session(
                db,
                session_id,
            )
        )


        ensure_learning_session_access(
            current_user=
                current_user,

            learning_session=
                learning_session,
        )


        complete_learning_session(

            db=db,

            session=
                learning_session,

            reason=
                payload.reason,
        )


        return (
            get_learning_session_summary(

                db=db,

                session_id=
                    session_id,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

@router.get(
    "/sessions/student/{student_code}"
)
def student_session_history(

    student_code: str,

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "STUDENT",
            "FACULTY",
            "ADMIN",
        )
    ),

    db: Session = Depends(
        get_db
    ),
):

    ensure_student_code_access(
        current_user=
            current_user,

        student_code=
            student_code,

        db=db,
    )


    try:

        return (
            get_student_learning_sessions(

                db=db,

                student_code=
                    student_code,

                limit=
                    limit,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
