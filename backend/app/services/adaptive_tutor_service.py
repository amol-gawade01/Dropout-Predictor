from sqlalchemy.orm import Session

from agents.tutor_graph import (
    tutor_graph,
)

from backend.app.db.models import (
    Concept,
    SocraticDialogueLog,
    Student,
    StudentConceptMastery,
)

from tutor.llm_evaluator import (
    evaluate_answer,
)

from tutor.question_bank import (
    get_question,
)

from tutor.llm_socratic import (
    generate_socratic_response,
)


MASTERY_THRESHOLD = 0.80


def process_adaptive_attempt(

    db: Session,

    student_code: str,

    question_id: str,

    student_answer: str,

    language_code: str = "en-IN",
):

    # ========================================================
    # STUDENT
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
    # QUESTION
    # ========================================================

    question_data = (
        get_question(
            question_id
        )
    )

    if question_data is None:

        raise ValueError(
            "Question not found"
        )


    # ========================================================
    # CONCEPT
    # ========================================================

    concept = db.get(

        Concept,

        question_data[
            "concept_id"
        ],
    )

    if concept is None:

        raise ValueError(
            "Concept not found"
        )


    # ========================================================
    # MASTERY
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

    if mastery is None:

        mastery = (
            StudentConceptMastery(

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
        )

        db.add(mastery)

        db.flush()


    mastery_before = float(
        mastery.mastery_prob
    )


    # ========================================================
    # GEMINI EVALUATION
    # ========================================================

    evaluation = evaluate_answer(

        question=
            question_data[
                "question"
            ],

        expected_answer=
            question_data[
                "expected_answer"
            ],

        student_answer=
            student_answer,

        mastery_prob=
            mastery_before,
    )


    # ========================================================
    # LANGGRAPH
    # ========================================================

    graph_result = (
        tutor_graph.invoke(
            {

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
                    question_data[
                        "question"
                    ],

                "student_answer":
                    student_answer,

                "is_correct":
                    evaluation
                    .is_correct,

                "mastery_before":
                    mastery_before,

                "evaluated_diagnosis":
                    evaluation
                    .diagnosis,

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
        )
    )
    # ========================================================
    # PERSONALIZED SOCRATIC RESPONSE
    # ========================================================

    prerequisite_name = None

    if concept.prerequisite_concept_id:

        prerequisite = db.get(
            Concept,
            concept.prerequisite_concept_id,
        )

        if prerequisite:

            prerequisite_name = (
                prerequisite.topic_name
            )

    try:

        socratic_response = (
            generate_socratic_response(

                concept_name=
                    concept.topic_name,

                question=
                    question_data[
                        "question"
                    ],

                student_answer=
                    student_answer,

                diagnosis=
                    graph_result[
                        "diagnosis"
                    ],

                tutor_strategy=
                    graph_result[
                        "tutor_strategy"
                    ],

                mastery_prob=
                    mastery_before,

                misconception=
                    evaluation
                    .misconception,

                prerequisite_name=
                    prerequisite_name,

                language_code=
                    language_code,
            )
        )

    except Exception as exc:

        print(
            "Socratic generation failed:",
            exc,
        )

        socratic_response = None

    mastery_after = float(
        graph_result[
            "mastery_after"
        ]
    )

    # ========================================================
    # FINAL SOCRATIC RESPONSE
    # ========================================================

    if socratic_response:

        final_tutor_message = (
            socratic_response.message
        )

        follow_up_question = (
            socratic_response
            .follow_up_question
        )

        encouragement = (
            socratic_response
            .encouragement
        )

    else:

        final_tutor_message = (
            graph_result[
                "tutor_message"
            ]
        )

        follow_up_question = None

        encouragement = None  

    # ========================================================
    # BUILD DIALOGUE TEXT FOR DATABASE
    # ========================================================

    dialogue_parts = [
        final_tutor_message
    ]

    if follow_up_question:

        dialogue_parts.append(
            "Follow-up: "
            + follow_up_question
        )

    if encouragement:

        dialogue_parts.append(
            "Encouragement: "
            + encouragement
        )

    socratic_prompt_returned = (
        "\n\n".join(
            dialogue_parts
        )
    )


    # ========================================================
    # UPDATE MASTERY
    # ========================================================

    mastery.mastery_prob = (
        mastery_after
    )

    mastery.total_attempts += 1

    if evaluation.is_correct:

        mastery.consecutive_correct += 1

    else:

        mastery.consecutive_correct = 0


     # ========================================================
    # SAVE SOCRATIC DIALOGUE LOG
    # ========================================================

    dialogue_log = (
        SocraticDialogueLog(

            student_id=
                student.student_id,

            concept_id=
                concept.concept_id,

            student_raw_input=
                student_answer,

            language_code=
                language_code,

            diagnosed_error=
                evaluation.diagnosis,

            socratic_prompt_returned=
                socratic_prompt_returned,

            mastery_prior=
                mastery_before,

            mastery_post=
                mastery_after,
        )
    )

    db.add(
        dialogue_log
    )


    db.commit()

    db.refresh(
        mastery
    )
    db.refresh(
        dialogue_log
    )

# ========================================================
    # PREREQUISITE RECOMMENDATION
    # ========================================================

    recommended_concept = None

    if (
        graph_result["route"]
        == "prerequisite"
        and concept.prerequisite_concept_id
    ):

        recommended_concept = {
            "concept_id":
                concept.prerequisite_concept_id,

            "topic_name":
                prerequisite_name,
        }


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "interaction_id":
            str(
                dialogue_log
                .interaction_id
            ),

        "student_code":
            student.student_code,

        "question": {

            "question_id":
                question_data[
                    "question_id"
                ],

            "concept_id":
                concept.concept_id,

            "text":
                question_data[
                    "question"
                ],

            "difficulty":
                question_data[
                    "difficulty"
                ],
        },

        "evaluation": {

            "is_correct":
                evaluation.is_correct,

            "diagnosis":
                evaluation.diagnosis,

            "confidence":
                evaluation.confidence,

            "misconception":
                evaluation.misconception,

            "reasoning_summary":
                evaluation.reasoning_summary,
        },

        "tutor": {

            "route":
                graph_result[
                    "route"
                ],

            "strategy":
                graph_result[
                    "tutor_strategy"
                ],

            "message":
                final_tutor_message,

            "follow_up_question":
                follow_up_question,

            "encouragement":
                encouragement,

            "prerequisite_concept":
                prerequisite_name,
        },

        "recommended_concept":
            recommended_concept,

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
                mastery.consecutive_correct,
        },

        "language_code":
            language_code,
    }
