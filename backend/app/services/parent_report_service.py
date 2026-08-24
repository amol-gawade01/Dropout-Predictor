from datetime import date
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from sqlalchemy.orm import Session

from backend.app.db.models import (
    Concept,
    InterventionTask,
    RiskInference,
    Student,
    StudentConceptMastery,
    StudentFeatureSnapshot,
    StudentLearningSession,
)


# -------------------------------------------------
# Support wording
# -------------------------------------------------

SUPPORT_LABELS = {
    "LOW":
        "On Track",

    "MODERATE":
        "Extra Support Recommended",

    "CRITICAL":
        "High Support Recommended",
}


def get_support_label(
    risk_tier: str,
) -> str:

    return SUPPORT_LABELS.get(
        risk_tier,
        "Not Evaluated",
    )


# -------------------------------------------------
# Normalize SHAP factor structure
# -------------------------------------------------

def normalize_factors(
    value,
):

    if not value:
        return []

    factors = []

    if isinstance(
        value,
        list,
    ):

        for item in value:

            if not isinstance(
                item,
                dict,
            ):
                continue

            factor = (
                item.get("factor")
                or item.get("name")
                or item.get(
                    "risk_factor"
                )
            )

            percentage = (
                item.get(
                    "contribution_percentage"
                )
            )

            if percentage is None:

                contribution = (
                    item.get(
                        "contribution"
                    )
                )

                if contribution is not None:

                    percentage = (
                        abs(
                            float(
                                contribution
                            )
                        )
                        * 100
                    )

            if (
                factor
                and percentage
                is not None
            ):

                factors.append(
                    {
                        "factor":
                            str(
                                factor
                            ),

                        "percentage":
                            round(
                                float(
                                    percentage
                                ),
                                2,
                            ),
                    }
                )

    elif isinstance(
        value,
        dict,
    ):

        for factor, contribution \
                in value.items():

            try:

                percentage = (
                    abs(
                        float(
                            contribution
                        )
                    )
                    * 100
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            factors.append(
                {
                    "factor":
                        str(
                            factor
                        ),

                    "percentage":
                        round(
                            percentage,
                            2,
                        ),
                }
            )

    return factors[:5]


# -------------------------------------------------
# Collect report data
# -------------------------------------------------

def collect_parent_report_data(
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

    if not student:
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
            RiskInference.evaluated_at
            .desc()
        )
        .first()
    )

    if not latest_risk:

        raise ValueError(
            "Student has not been "
            "evaluated by EWS yet"
        )


    if latest_risk.risk_tier not in {
        "MODERATE",
        "CRITICAL",
    }:

        raise ValueError(
            "Parent support reports "
            "are currently available "
            "only for MODERATE or "
            "CRITICAL students"
        )


    latest_snapshot = (
        db.query(
            StudentFeatureSnapshot
        )
        .filter(
            StudentFeatureSnapshot
            .student_id
            == student.student_id
        )
        .order_by(
            StudentFeatureSnapshot
            .week_start_date
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
            ==
            StudentConceptMastery
            .concept_id,
        )
        .filter(
            StudentConceptMastery
            .student_id
            == student.student_id
        )
        .all()
    )


    mastery = []

    for state, concept \
            in mastery_rows:

        mastery.append(
            {
                "concept_id":
                    concept.concept_id,

                "topic_name":
                    concept.topic_name,

                "mastery_percentage":
                    round(
                        float(
                            state.mastery_prob
                            or 0
                        )
                        * 100,
                        1,
                    ),

                "attempts":
                    state.total_attempts,
            }
        )


    session_count = (
        db.query(
            StudentLearningSession
        )
        .filter(
            StudentLearningSession
            .student_id
            == student.student_id
        )
        .count()
    )


    completed_sessions = (
        db.query(
            StudentLearningSession
        )
        .filter(
            StudentLearningSession
            .student_id
            == student.student_id,

            StudentLearningSession
            .status
            == "COMPLETED",
        )
        .count()
    )


    intervention = (
        db.query(
            InterventionTask
        )
        .filter(
            InterventionTask.student_id
            == student.student_id
        )
        .order_by(
            InterventionTask.updated_at
            .desc()
        )
        .first()
    )


    history_rows = (
        db.query(
            RiskInference
        )
        .filter(
            RiskInference.student_id
            == student.student_id
        )
        .order_by(
            RiskInference.evaluated_at
            .desc()
        )
        .limit(8)
        .all()
    )

    history_rows.reverse()


    risk_history = [

        {
            "date":
                item.evaluated_at
                .strftime(
                    "%d %b"
                ),

            "score":
                round(
                    float(
                        item.risk_score
                    )
                    * 100,
                    1,
                ),
        }

        for item
        in history_rows
    ]


    return {

        "student":
            student,

        "risk":
            latest_risk,

        "snapshot":
            latest_snapshot,

        "support_level":
            get_support_label(
                latest_risk.risk_tier
            ),

        "factors":
            normalize_factors(
                latest_risk.top_factors
            ),

        "mastery":
            mastery,

        "session_count":
            session_count,

        "completed_sessions":
            completed_sessions,

        "risk_history":
            risk_history,

        "intervention":
            intervention,
    }


# -------------------------------------------------
# Chart generation
# -------------------------------------------------

def build_factor_chart(
    factors,
):

    if not factors:
        return None

    names = [
        item["factor"]
        for item in factors
    ]

    values = [
        item["percentage"]
        for item in factors
    ]

    buffer = BytesIO()

    fig, ax = plt.subplots(
        figsize=(7, 3.2)
    )

    ax.barh(
        names[::-1],
        values[::-1],
    )

    ax.set_xlabel(
        "Relative model contribution (%)"
    )

    ax.set_title(
        "Top Predictive Risk Factors"
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)

    fig.tight_layout()

    fig.savefig(
        buffer,
        format="png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return buffer


def build_mastery_chart(
    mastery,
):

    if not mastery:
        return None

    names = [
        item["topic_name"]
        for item in mastery
    ]

    values = [
        item[
            "mastery_percentage"
        ]
        for item in mastery
    ]

    buffer = BytesIO()

    fig, ax = plt.subplots(
        figsize=(7, 3.2)
    )

    ax.barh(
        names[::-1],
        values[::-1],
    )

    ax.set_xlim(
        0,
        100,
    )

    ax.set_xlabel(
        "Mastery (%)"
    )

    ax.set_title(
        "Learning Mastery"
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)

    fig.tight_layout()

    fig.savefig(
        buffer,
        format="png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return buffer


def build_risk_history_chart(
    history,
):

    if len(history) < 2:
        return None

    labels = [
        item["date"]
        for item in history
    ]

    values = [
        item["score"]
        for item in history
    ]

    buffer = BytesIO()

    fig, ax = plt.subplots(
        figsize=(7, 3)
    )

    ax.plot(
        labels,
        values,
        marker="o",
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_ylabel(
        "Support score (%)"
    )

    ax.set_title(
        "Student Support Trend"
    )

    ax.spines[
        "top"
    ].set_visible(False)

    ax.spines[
        "right"
    ].set_visible(False)

    fig.tight_layout()

    fig.savefig(
        buffer,
        format="png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)

    buffer.seek(0)

    return buffer


# -------------------------------------------------
# PDF generation
# -------------------------------------------------

def generate_parent_report_pdf(
    db: Session,
    student_code: str,
):

    data = (
        collect_parent_report_data(
            db=db,
            student_code=student_code,
        )
    )

    student = data["student"]

    snapshot = data[
        "snapshot"
    ]

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,

        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = (
        getSampleStyleSheet()
    )

    title_style = (
        ParagraphStyle(
            "ReportTitle",
            parent=styles[
                "Title"
            ],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=8,
        )
    )

    heading_style = (
        ParagraphStyle(
            "SectionHeading",
            parent=styles[
                "Heading2"
            ],
            fontSize=13,
            spaceBefore=12,
            spaceAfter=7,
        )
    )

    body_style = (
        styles["BodyText"]
    )

    story = []


    story.append(
        Paragraph(
            "Student Support Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "AI Student Success Platform",
            styles["Heading3"],
        )
    )

    story.append(
        Spacer(
            1,
            10,
        )
    )


    info = [

        [
            "Student",
            student.display_name,
        ],

        [
            "Student Code",
            student.student_code,
        ],

        [
            "Program",
            student.program_stream
            or "-",
        ],

        [
            "Report Date",
            date.today()
            .strftime(
                "%d %B %Y"
            ),
        ],
    ]


    info_table = Table(
        info,
        colWidths=[
            4 * cm,
            12 * cm,
        ],
    )

    info_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F3F4F6"
                    ),
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#E5E7EB"
                    ),
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        info_table
    )

    story.append(
        Spacer(
            1,
            14,
        )
    )


    story.append(
        Paragraph(
            "Current Support Status",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>{data['support_level']}</b>",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            "This status is generated by "
            "a predictive decision-support "
            "system and should be reviewed "
            "with academic and faculty context.",
            body_style,
        )
    )


    if snapshot:

        story.append(
            Paragraph(
                "Academic Snapshot",
                heading_style,
            )
        )

        academic = [

            [
                "Current GPA",
                str(
                    snapshot.current_gpa
                ),
            ],

            [
                "Attendance",
                (
                    f"{snapshot.attendance_pct}%"
                ),
            ],

            [
                "Assignments Completed",
                (
                    f"{snapshot.assignment_completion_pct}%"
                ),
            ],

            [
                "Failed Subjects",
                str(
                    snapshot.failed_subjects
                ),
            ],

            [
                "Backlogs",
                str(
                    snapshot.backlog_count
                ),
            ],
        ]

        table = Table(
            academic,
            colWidths=[
                7.5 * cm,
                7.5 * cm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#E5E7EB"
                        ),
                    ),

                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(
            table
        )


    factor_chart = (
        build_factor_chart(
            data["factors"]
        )
    )

    if factor_chart:

        story.append(
            Paragraph(
                "Predictive Risk Factors",
                heading_style,
            )
        )

        story.append(
            Image(
                factor_chart,
                width=16 * cm,
                height=7.3 * cm,
            )
        )

        story.append(
            Paragraph(
                "These are predictive model "
                "signals, not proven causes "
                "of student dropout.",
                body_style,
            )
        )


    mastery_chart = (
        build_mastery_chart(
            data["mastery"]
        )
    )

    if mastery_chart:

        story.append(
            Paragraph(
                "Learning Progress",
                heading_style,
            )
        )

        story.append(
            Image(
                mastery_chart,
                width=16 * cm,
                height=7.3 * cm,
            )
        )


    story.append(
        Paragraph(
            "Learning Activity",
            heading_style,
        )
    )

    learning_table = Table(
        [
            [
                "Learning sessions",
                data[
                    "session_count"
                ],
            ],

            [
                "Completed sessions",
                data[
                    "completed_sessions"
                ],
            ],

            [
                "Tracked concepts",
                len(
                    data[
                        "mastery"
                    ]
                ),
            ],
        ],
        colWidths=[
            8 * cm,
            7 * cm,
        ],
    )

    learning_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#E5E7EB"
                    ),
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        learning_table
    )


    risk_chart = (
        build_risk_history_chart(
            data[
                "risk_history"
            ]
        )
    )

    if risk_chart:

        story.append(
            Paragraph(
                "Support Trend",
                heading_style,
            )
        )

        story.append(
            Image(
                risk_chart,
                width=16 * cm,
                height=6.8 * cm,
            )
        )


    intervention = data[
        "intervention"
    ]

    if intervention:

        story.append(
            Paragraph(
                "Faculty Support Plan",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                (
                    "<b>Support area:</b> "
                    f"{intervention.routed_domain}"
                ),
                body_style,
            )
        )

        if (
            intervention
            .remediation_plan
        ):

            story.append(
                Paragraph(
                    (
                        "<b>Recommended "
                        "support:</b> "
                        f"{intervention.remediation_plan}"
                    ),
                    body_style,
                )
            )


    story.append(
        Spacer(
            1,
            15,
        )
    )

    story.append(
        Paragraph(
            "<b>Important:</b> This report "
            "is intended to support discussion "
            "between the student, guardian and "
            "institution. AI predictions and "
            "model explanations should not be "
            "treated as confirmed causes or "
            "final academic decisions.",
            body_style,
        )
    )


    document.build(
        story
    )

    pdf_bytes = (
        buffer.getvalue()
    )

    buffer.close()

    filename = (
        f"{student.student_code}_"
        f"student_support_report_"
        f"{date.today().isoformat()}"
        f".pdf"
    )

    return (
        pdf_bytes,
        filename,
        data,
    )