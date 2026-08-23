from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    SocraticDialogueLog,
    Student,
)

from tutor.bkt import update_mastery
from tutor.diagnostic import diagnose_attempt


def process_tutor_attempt(
    db: Session,
    student_code: str,
    concept_id: str,
    student_answer: str,
    is_correct: bool,
    language_code: str = "en-IN",
):
    """
    Process one Tutor attempt.

    Phase 3:
    - Find student
    - Find concept
    - Diagnose response
    - Update BKT mastery
    - Save Socratic dialogue log
    """

    # --------------------------------------------------------
    # 1. FIND STUDENT
    # --------------------------------------------------------

    student = (
        db.query(Student)
        .filter(
            Student.student_code == student_code
        )
        .first()
    )

    if student is None:
        raise ValueError(
            f"Student '{student_code}' not found."
        )

    # --------------------------------------------------------
    # 2. FIND CONCEPT
    # --------------------------------------------------------

    concept = db.get(
        Concept,
        concept_id,
    )

    if concept is None:
        raise ValueError(
            f"Concept '{concept_id}' not found."
        )

    # --------------------------------------------------------
    # 3. GET CURRENT MASTERY
    # --------------------------------------------------------

    from backend.app.db.models import (
        StudentConceptMastery,
    )

    mastery_record = (
        db.query(StudentConceptMastery)
        .filter(
            StudentConceptMastery.student_id
            == student.student_id,

            StudentConceptMastery.concept_id
            == concept_id,
        )
        .first()
    )

    if mastery_record is None:

        mastery_before = 0.20

        mastery_record = StudentConceptMastery(
            student_id=student.student_id,
            concept_id=concept_id,
            mastery_prob=0.20,
            total_attempts=0,
            consecutive_correct=0,
        )

        db.add(mastery_record)

        db.flush()

    else:

        mastery_before = float(
            mastery_record.mastery_prob
        )

    # --------------------------------------------------------
    # 4. DIAGNOSE ANSWER
    # --------------------------------------------------------

    diagnosis = diagnose_attempt(
        student_answer=student_answer,
        is_correct=is_correct,
        mastery_prob=mastery_before,
    )

    # --------------------------------------------------------
    # 5. UPDATE BKT
    # --------------------------------------------------------

    mastery_after = update_mastery(
        prior_mastery=mastery_before,
        correct=is_correct,
    )

    # --------------------------------------------------------
    # 6. UPDATE MASTERY RECORD
    # --------------------------------------------------------

    mastery_record.mastery_prob = mastery_after

    mastery_record.total_attempts += 1

    if is_correct:
        mastery_record.consecutive_correct += 1
    else:
        mastery_record.consecutive_correct = 0

    # --------------------------------------------------------
    # 7. GENERATE PHASE 3 SOCRATIC RESPONSE
    # --------------------------------------------------------

    if diagnosis == "PREREQUISITE_GAP":

        socratic_prompt = (
            "Let's revisit the prerequisite concept first. "
            "What do you already remember about the basic idea?"
        )

    elif diagnosis == "CONCEPTUAL_MISUNDERSTANDING":

        socratic_prompt = (
            "Think about the definition of the concept. "
            "Which fundamental property should your answer satisfy?"
        )

    elif diagnosis == "MINOR_ERROR":

        socratic_prompt = (
            "You're close. Recheck the step where your "
            "reasoning changed. What assumption did you make?"
        )

    elif diagnosis == "CORRECT":

        socratic_prompt = (
            "Good work. Now explain why your answer is correct "
            "using the underlying concept."
        )

    else:

        socratic_prompt = (
            "That's okay. Tell me which part of the question "
            "is unclear, and we'll work through it together."
        )

    # --------------------------------------------------------
    # 8. SAVE SOCRATIC DIALOGUE LOG
    # --------------------------------------------------------

    dialogue_log = SocraticDialogueLog(

        student_id=student.student_id,

        concept_id=concept_id,

        student_raw_input=student_answer,

        language_code=language_code,

        diagnosed_error=diagnosis,

        socratic_prompt_returned=socratic_prompt,

        mastery_prior=mastery_before,

        mastery_post=mastery_after,
    )

    db.add(dialogue_log)

    # --------------------------------------------------------
    # 9. COMMIT EVERYTHING
    # --------------------------------------------------------

    db.commit()

    # --------------------------------------------------------
    # 10. RESPONSE
    # --------------------------------------------------------

    return {
        "student_code": student_code,

        "concept_id": concept_id,

        "diagnosis": diagnosis,

        "socratic_prompt": socratic_prompt,

        "mastery_before": mastery_before,

        "mastery_after": mastery_after,

        "mastery_change": round(
            mastery_after - mastery_before,
            4,
        ),

        "total_attempts":
            mastery_record.total_attempts,

        "consecutive_correct":
            mastery_record.consecutive_correct,

        "language_code": language_code,
    }