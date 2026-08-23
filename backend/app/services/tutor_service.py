from sqlalchemy.orm import Session

from agents.tutor_graph import (
    tutor_graph,
)

from backend.app.db.models import (
    Concept,
    Student,
    StudentConceptMastery,
)


MASTERY_THRESHOLD = 0.80


def process_tutor_attempt(
    db: Session,
    student_code: str,
    concept_id: str,
    question: str,
    student_answer: str,
    is_correct: bool,
    language_code: str = "en-IN",
):

    # ========================================================
    # 1. FIND STUDENT
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

        raise ValueError(
            "Student not found"
        )


    # ========================================================
    # 2. FIND CONCEPT
    # ========================================================

    concept = db.get(
        Concept,
        concept_id,
    )

    if concept is None:

        raise ValueError(
            "Concept not found"
        )


    # ========================================================
    # 3. GET EXISTING MASTERY
    # ========================================================

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


    # ========================================================
    # 4. CREATE MASTERY IF FIRST ATTEMPT
    # ========================================================

    if mastery is None:

        mastery = StudentConceptMastery(

            student_id=
                student.student_id,

            concept_id=
                concept.concept_id,

            mastery_prob=
                0.20,

            total_attempts=
                0,

            consecutive_correct=
                0,
        )

        db.add(
            mastery
        )

        db.flush()


    mastery_before = float(
        mastery.mastery_prob
    )


    # ========================================================
    # 5. SEND STATE TO LANGGRAPH
    # ========================================================

    graph_input = {

        "student_id":
            str(
                student.student_id
            ),

        "concept_id":
            concept.concept_id,

        "prerequisite_concept_id":
            concept
            .prerequisite_concept_id,

        "question":
            question,

        "student_answer":
            student_answer,

        "is_correct":
            is_correct,

        "mastery_before":
            mastery_before,

        "diagnosis":
            None,

        "route":
            None,

        "tutor_strategy":
            None,

        "tutor_message":
            None,

        "mastery_after":
            None,
    }


    graph_result = (
        tutor_graph.invoke(
            graph_input
        )
    )


    # ========================================================
    # 6. GET NEW BKT MASTERY
    # ========================================================

    mastery_after = float(
        graph_result[
            "mastery_after"
        ]
    )


    # ========================================================
    # 7. UPDATE DATABASE
    # ========================================================

    mastery.mastery_prob = (
        mastery_after
    )

    mastery.total_attempts += 1


    if is_correct:

        mastery.consecutive_correct += 1

    else:

        mastery.consecutive_correct = 0


    db.commit()

    db.refresh(
        mastery
    )


    # ========================================================
    # 8. RETURN RESULT
    # ========================================================

    return {

        "student_code":
            student.student_code,

        "concept": {

            "concept_id":
                concept.concept_id,

            "topic_name":
                concept.topic_name,

            "prerequisite_concept_id":
                concept
                .prerequisite_concept_id,
        },

        "question":
            question,

        "student_answer":
            student_answer,

        "is_correct":
            is_correct,

        "diagnosis":
            graph_result[
                "diagnosis"
            ],

        "route":
            graph_result[
                "route"
            ],

        "tutor_strategy":
            graph_result[
                "tutor_strategy"
            ],

        "tutor_message":
            graph_result[
                "tutor_message"
            ],

        "mastery": {

            "before":
                mastery_before,

            "after":
                mastery_after,

            "change":
                round(
                    mastery_after
                    - mastery_before,
                    4,
                ),

            "mastered":
                mastery_after
                >= MASTERY_THRESHOLD,

            "total_attempts":
                mastery.total_attempts,

            "consecutive_correct":
                mastery
                .consecutive_correct,
        },

        "language_code":
            language_code,
    }