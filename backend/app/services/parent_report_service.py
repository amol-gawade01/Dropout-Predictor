import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import make_msgid
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

from backend.app.core.config import get_settings
from backend.app.db.models import (
    ParentReportDelivery,
    RiskInference,
    Student,
    StudentFeatureSnapshot,
    StudentGuardian,
)


def _context(db, code):
    student = db.query(Student).filter(Student.student_code == code).first()
    if not student:
        raise ValueError("Student not found")
    snapshot = (
        db.query(StudentFeatureSnapshot)
        .filter(StudentFeatureSnapshot.student_id == student.student_id)
        .order_by(StudentFeatureSnapshot.week_start_date.desc())
        .first()
    )
    inference = (
        db.query(RiskInference)
        .filter(RiskInference.student_id == student.student_id)
        .order_by(RiskInference.evaluated_at.desc())
        .first()
    )
    guardians = (
        db.query(StudentGuardian)
        .filter(
            StudentGuardian.student_id == student.student_id, StudentGuardian.is_active.is_(True)
        )
        .all()
    )
    return student, snapshot, inference, guardians


def list_guardians(db, code):
    student, _, inference, guardians = _context(db, code)
    deliveries = (
        db.query(ParentReportDelivery)
        .filter(ParentReportDelivery.student_id == student.student_id)
        .order_by(ParentReportDelivery.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "student_code": code,
        "report_available": inference is not None,
        "guardians": [
            {
                "guardian_id": str(g.guardian_id),
                "guardian_name": g.guardian_name,
                "relationship": g.relationship,
                "email_address": g.email_address,
                "email_opt_in": g.email_opt_in,
            }
            for g in guardians
        ],
        "recent_deliveries": [
            {
                "delivery_id": str(d.delivery_id),
                "status": d.status,
                "created_at": d.created_at,
                "sent_at": d.sent_at,
                "failure_reason": d.failure_reason,
            }
            for d in deliveries
        ],
    }


def build_student_report_pdf(db, code, note=None):
    student, snapshot, inference, guardians = _context(db, code)
    if not inference:
        raise ValueError("Evaluate this student before generating a report")
    styles, out = getSampleStyleSheet(), BytesIO()
    rows = [
        ["Student", student.display_name],
        ["Student code", code],
        ["Programme", student.program_stream or "Not recorded"],
        ["Risk level", inference.risk_tier],
        ["Risk score", f"{float(inference.risk_score) * 100:.1f}%"],
    ]
    if snapshot:
        rows += [
            ["Attendance", f"{snapshot.attendance_pct:.1f}%"],
            ["Current GPA", f"{snapshot.current_gpa:.2f}"],
            ["Assignments", f"{snapshot.assignment_completion_pct:.1f}%"],
        ]
    story = [
        Paragraph("EDUCOMPASS", styles["Title"]),
        Paragraph("Student Progress &amp; Support Report", styles["Heading2"]),
        Spacer(1, 10),
        Table(rows, colWidths=[55 * mm, 103 * mm]),
    ]
    if note:
        story += [
            Paragraph("Faculty note", styles["Heading2"]),
            Paragraph(note, styles["BodyText"]),
        ]
    story += [
        Spacer(1, 12),
        Paragraph(
            "This report supports a constructive conversation with the student.", styles["BodyText"]
        ),
    ]
    SimpleDocTemplate(out, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm).build(story)
    return out.getvalue(), (student, inference, guardians)


def _send_email(recipient, pdf, filename, student_name):
    s = get_settings()
    if not s.gmail_address or not s.gmail_app_password:
        raise RuntimeError("Gmail SMTP is not configured on the server")
    message = EmailMessage()
    message["From"] = s.gmail_address
    message["To"] = recipient
    message["Subject"] = f"EduCompass progress report for {student_name}"
    message_id = make_msgid(domain=s.gmail_address.partition("@")[2] or None)
    message["Message-ID"] = message_id
    message.set_content(
        f"Dear Guardian,\n\nPlease find attached the EduCompass progress and support "
        f"report for {student_name}.\n\nRegards,\nEduCompass Faculty Team"
    )
    message.add_attachment(pdf, maintype="application", subtype="pdf", filename=filename)
    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=30) as client:
        client.starttls()
        client.login(s.gmail_address, s.gmail_app_password)
        client.send_message(message)
    return message_id


def send_parent_report(db, code, guardian_id, note, user):
    pdf, (student, inference, guardians) = build_student_report_pdf(db, code, note)
    guardian = next((g for g in guardians if str(g.guardian_id) == guardian_id), None)
    if not guardian:
        raise ValueError("Guardian not found for this student")
    if not guardian.email_address:
        raise ValueError("Guardian email address has not been recorded")
    if not guardian.email_opt_in or not guardian.consent_recorded_at:
        raise ValueError("Guardian email consent has not been recorded")
    d = ParentReportDelivery(
        student_id=student.student_id,
        guardian_id=guardian.guardian_id,
        inference_id=inference.inference_id,
        approved_by=user.user_id,
        language_code=guardian.preferred_language,
        status="SENDING",
        mentor_note=note,
    )
    db.add(d)
    db.commit()
    try:
        d.email_message_id = _send_email(
            guardian.email_address,
            pdf,
            f"EduCompass-{code}-report.pdf",
            student.display_name,
        )
        d.status = "SENT"
        d.sent_at = datetime.now(UTC)
    except Exception as exc:
        d.status = "FAILED"
        d.failure_reason = str(exc)[:1000]
        db.commit()
        raise RuntimeError(d.failure_reason) from exc
    db.commit()
    db.refresh(d)
    return d
