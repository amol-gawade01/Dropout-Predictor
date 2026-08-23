from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    InterventionTask,
    RiskInference,
    Student,
    StudentConceptMastery,
)


MASTERY_THRESHOLD = 0.80


ACADEMIC_RISK_FACTORS = {
    "Academic Difficulty",
    "Low Learning Engagement",
    "Attendance Decline",
    "Transition / Language / Prerequisite Gap",
    "Wellbeing / Support Need",
}


# ============================================================
# FIND STUDENT
# ============================================================


def get_student_by_code(
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
# LATEST RISK
# ============================================================


def get_latest_risk(
    db: Session,
    student_id,
):

    return (
        db.query(RiskInference)
        .filter(
            RiskInference.student_id
            == student_id
        )
        .order_by(
            RiskInference
            .evaluated_at
            .desc()
        )
        .first()
    )


# ============================================================
# LATEST INTERVENTION
# ============================================================


def get_latest_intervention(
    db: Session,
    student_id,
):

    return (
        db.query(InterventionTask)
        .filter(
            InterventionTask.student_id
            == student_id
        )
        .order_by(
            InterventionTask
            .updated_at
            .desc()
        )
        .first()
    )


# ============================================================
# EXTRACT IMPORTANT EWS FACTORS
# ============================================================


def extract_academic_risk_factors(
    risk: RiskInference | None,
):

    if risk is None:
        return []

    factors = (
        risk.top_factors
        or []
    )

    academic_factors = []

    for factor in factors:

        factor_name = (
            factor.get("factor")
        )

        if (
            factor_name
            in ACADEMIC_RISK_FACTORS
        ):

            academic_factors.append(
                {
                    "factor":
                        factor_name,

                    "contribution_percentage":
                        factor.get(
                            "contribution_percentage",
                            0,
                        ),
                }
            )

    return academic_factors


# ============================================================
# CONCEPT DEPTH
# ============================================================


def calculate_concept_depth(
    concept_id: str,
    concept_map: dict,
    visited=None,
):

    if visited is None:
        visited = set()

    if concept_id in visited:
        return 0

    visited.add(
        concept_id
    )

    concept = concept_map.get(
        concept_id
    )

    if concept is None:
        return 0

    prerequisite_id = (
        concept.prerequisite_concept_id
    )

    if prerequisite_id is None:
        return 0

    return (
        1
        + calculate_concept_depth(
            prerequisite_id,
            concept_map,
            visited,
        )
    )


# ============================================================
# GET WEAK CONCEPTS
# ============================================================


def get_weak_concepts(
    db: Session,
    student_id,
    limit: int = 3,
):

    concepts = (
        db.query(Concept)
        .all()
    )

    mastery_rows = (
        db.query(
            StudentConceptMastery
        )
        .filter(
            StudentConceptMastery.student_id
            == student_id
        )
        .all()
    )

    mastery_map = {
        row.concept_id: row
        for row in mastery_rows
    }

    concept_map = {
        concept.concept_id:
            concept
        for concept in concepts
    }

    weak = []

    for concept in concepts:

        mastery = mastery_map.get(
            concept.concept_id
        )

        if mastery:

            mastery_prob = float(
                mastery.mastery_prob
            )

            attempts = (
                mastery.total_attempts
            )

        else:

            # New/unseen concepts use
            # the same default as Tutor.
            mastery_prob = 0.20
            attempts = 0

        if (
            mastery_prob
            >= MASTERY_THRESHOLD
        ):
            continue

        depth = (
            calculate_concept_depth(
                concept.concept_id,
                concept_map,
            )
        )

        weak.append(
            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "mastery_probability":
                    mastery_prob,

                "mastery_percentage":
                    round(
                        mastery_prob
                        * 100,
                        2,
                    ),

                "total_attempts":
                    attempts,

                "prerequisite_concept_id":
                    concept
                    .prerequisite_concept_id,

                "concept_depth":
                    depth,
            }
        )

    # Lower mastery first.
    #
    # If mastery is equal, recommend
    # more foundational concepts first.

    weak.sort(
        key=lambda item: (
            item[
                "mastery_probability"
            ],

            item[
                "concept_depth"
            ],

            item[
                "topic_name"
            ],
        )
    )

    return weak[:limit]


# ============================================================
# DETERMINE PRIORITY
# ============================================================


def recommendation_priority(
    risk: RiskInference | None,
):

    if risk is None:
        return "NORMAL"

    if (
        risk.risk_tier
        == "CRITICAL"
    ):
        return "HIGH"

    if (
        risk.risk_tier
        == "MODERATE"
    ):
        return "MEDIUM"

    return "NORMAL"


# ============================================================
# BUILD RECOMMENDATIONS
# ============================================================


def build_student_recommendations(
    db: Session,
    student_code: str,
    limit: int = 3,
):

    student = get_student_by_code(
        db,
        student_code,
    )

    risk = get_latest_risk(
        db,
        student.student_id,
    )

    academic_risk_factors = (
        extract_academic_risk_factors(
            risk
        )
    )

    weak_concepts = (
        get_weak_concepts(
            db,
            student.student_id,
            limit=limit,
        )
    )

    priority = (
        recommendation_priority(
            risk
        )
    )

    recommendations = []

    for concept in weak_concepts:

        if academic_risk_factors:

            reason = (
                "Academic or learning risk was "
                "detected by the Early Warning "
                "System, and this concept currently "
                "has low mastery."
            )

        else:

            reason = (
                "This concept currently has "
                "low mastery and is recommended "
                "for additional practice."
            )

        recommendations.append(
            {
                "type":
                    "TUTOR_PRACTICE",

                "priority":
                    priority,

                "concept_id":
                    concept[
                        "concept_id"
                    ],

                "topic_name":
                    concept[
                        "topic_name"
                    ],

                "mastery_percentage":
                    concept[
                        "mastery_percentage"
                    ],

                "total_attempts":
                    concept[
                        "total_attempts"
                    ],

                "reason":
                    reason,

                "action": {
                    "endpoint": (
                        "/api/v1/tutor/"
                        "next-question/"
                        f"{student.student_code}/"
                        f"{concept['concept_id']}"
                    )
                },
            }
        )

    return {
        "student":
            student,

        "risk":
            risk,

        "academic_risk_factors":
            academic_risk_factors,

        "recommendations":
            recommendations,
    }