from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.app.core.auth import require_roles
from backend.app.db.models import UserAccount
from backend.app.db.session import get_db
from backend.app.schemas.parent_report import SendParentReportRequest
from backend.app.services.parent_report_service import (
    build_student_report_pdf,
    list_guardians,
    send_parent_report,
)

router = APIRouter(prefix="/faculty/reports", tags=["Faculty Parent Reports"])


@router.get("/{student_code}")
def details(
    student_code: str,
    _user: UserAccount = Depends(require_roles("FACULTY", "ADMIN")),
    db: Session = Depends(get_db),
):
    try:
        return list_guardians(db, student_code)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/{student_code}/preview.pdf")
def preview(
    student_code: str,
    _user: UserAccount = Depends(require_roles("FACULTY", "ADMIN")),
    db: Session = Depends(get_db),
):
    try:
        content, _ = build_student_report_pdf(db, student_code)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="EduCompass-{student_code}-report.pdf"'},
    )


@router.post("/{student_code}/send")
def send(
    student_code: str,
    payload: SendParentReportRequest,
    current_user: UserAccount = Depends(require_roles("FACULTY", "ADMIN")),
    db: Session = Depends(get_db),
):
    try:
        delivery = send_parent_report(
            db, student_code, payload.guardian_id, payload.mentor_note, current_user
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc
    return {
        "delivery_id": str(delivery.delivery_id),
        "status": delivery.status,
        "sent_at": delivery.sent_at,
        "message": "Report emailed to the guardian",
    }
