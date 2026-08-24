from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
)

from sqlalchemy.orm import Session


from backend.app.core.auth import (
    require_roles,
)

from backend.app.db.models import (
    GuardianContact,
    ParentReportDelivery,
    Student,
    UserAccount,
)

from backend.app.db.session import (
    get_db,
)

from backend.app.schemas.parent_report import (
    GuardianResponse,
    GuardianUpsertRequest,
    ParentReportSendResponse,
)

from backend.app.services.parent_report_service import (
    generate_parent_report_pdf,
)

from backend.app.services.whatsapp_service import (
    WhatsAppServiceError,
    send_parent_report,
)


router = APIRouter(
    prefix="/faculty",
    tags=[
        "Faculty Parent Reports"
    ],
)

@router.put(
    "/students/{student_code}/guardian",
    response_model=GuardianResponse,
)
def upsert_guardian(
    student_code: str,
    payload: GuardianUpsertRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
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

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )


    guardian = (
        db.query(
            GuardianContact
        )
        .filter(
            GuardianContact.student_id
            == student.student_id,

            GuardianContact.is_primary
            == True,
        )
        .first()
    )


    if guardian:

        guardian.guardian_name = (
            payload.guardian_name
        )

        guardian.relationship = (
            payload.relationship
        )

        guardian.phone_number = (
            payload.phone_number
        )

        guardian.whatsapp_opt_in = (
            payload.whatsapp_opt_in
        )

    else:

        guardian = GuardianContact(

            student_id=
                student.student_id,

            guardian_name=
                payload.guardian_name,

            relationship=
                payload.relationship,

            phone_number=
                payload.phone_number,

            whatsapp_opt_in=
                payload.whatsapp_opt_in,

            is_primary=True,
        )

        db.add(
            guardian
        )


    db.commit()

    db.refresh(
        guardian
    )

    return guardian

@router.get(
    "/students/{student_code}/guardian",
    response_model=GuardianResponse,
)
def get_guardian(
    student_code: str,

    db: Session = Depends(
        get_db
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),
):

    guardian = (
        db.query(
            GuardianContact
        )
        .join(
            Student,
            Student.student_id
            ==
            GuardianContact.student_id,
        )
        .filter(
            Student.student_code
            == student_code,

            GuardianContact.is_primary
            == True,
        )
        .first()
    )

    if not guardian:

        raise HTTPException(
            status_code=404,
            detail=(
                "Guardian contact "
                "not found"
            ),
        )

    return guardian

@router.get(
    "/students/{student_code}"
    "/parent-report/preview"
)
def preview_parent_report(
    student_code: str,

    db: Session = Depends(
        get_db
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
    ),
):

    try:

        (
            pdf_bytes,
            filename,
            _,
        ) = generate_parent_report_pdf(
            db=db,
            student_code=student_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    return Response(

        content=pdf_bytes,

        media_type=
            "application/pdf",

        headers={
            "Content-Disposition":
                (
                    f'inline; '
                    f'filename="{filename}"'
                )
        },
    )

@router.post(
    "/students/{student_code}"
    "/parent-report/send",
    response_model=
        ParentReportSendResponse,
)
def send_parent_report_to_guardian(
    student_code: str,

    db: Session = Depends(
        get_db
    ),

    current_user: UserAccount = Depends(
        require_roles(
            "FACULTY",
            "ADMIN",
        )
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

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )


    guardian = (
        db.query(
            GuardianContact
        )
        .filter(
            GuardianContact.student_id
            == student.student_id,

            GuardianContact.is_primary
            == True,
        )
        .first()
    )


    if not guardian:

        raise HTTPException(
            status_code=400,
            detail=(
                "Add a guardian contact "
                "before sending a report"
            ),
        )


    if not guardian.whatsapp_opt_in:

        raise HTTPException(
            status_code=400,
            detail=(
                "Guardian has not opted in "
                "to WhatsApp communication"
            ),
        )


    try:

        (
            pdf_bytes,
            filename,
            report_data,
        ) = generate_parent_report_pdf(
            db=db,
            student_code=student_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


    risk = report_data[
        "risk"
    ]

    delivery = (
        ParentReportDelivery(

            student_id=
                student.student_id,

            guardian_id=
                guardian.guardian_id,

            risk_inference_id=
                risk.inference_id,

            generated_by_user_id=
                current_user.user_id,

            support_level=
                report_data[
                    "support_level"
                ],

            status=
                "SENDING",
        )
    )

    db.add(
        delivery
    )

    db.commit()

    db.refresh(
        delivery
    )


    try:

        whatsapp_result = (
            send_parent_report(

                phone_number=
                    guardian.phone_number,

                pdf_bytes=
                    pdf_bytes,

                filename=
                    filename,

                guardian_name=
                    guardian.guardian_name,

                student_name=
                    student.display_name,

                support_level=
                    report_data[
                        "support_level"
                    ],
            )
        )


        delivery.status = (
            "SENT"
        )

        delivery.whatsapp_message_id = (
            whatsapp_result[
                "message_id"
            ]
        )

        delivery.sent_at = (
            datetime.now(
                timezone.utc
            )
        )

        delivery.error_message = (
            None
        )

        db.commit()

        db.refresh(
            delivery
        )


    except WhatsAppServiceError \
            as exc:

        delivery.status = (
            "FAILED"
        )

        delivery.error_message = (
            str(exc)
        )

        db.commit()

        raise HTTPException(
            status_code=502,
            detail=(
                "WhatsApp delivery "
                f"failed: {exc}"
            ),
        ) from exc


    return ParentReportSendResponse(

        report_id=
            delivery.report_id,

        student_code=
            student.student_code,

        guardian_name=
            guardian.guardian_name,

        phone_number=
            guardian.phone_number,

        support_level=
            delivery.support_level,

        status=
            delivery.status,

        whatsapp_message_id=
            delivery
            .whatsapp_message_id,

        sent_at=
            delivery.sent_at,
    )