from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from backend.app.db.session import (
    get_db,
)

from backend.app.services.support_plan_service import (
    build_support_plan,
)


router = APIRouter(
    prefix="/integration",
    tags=["EWS + Tutor Integration"],
)


@router.get(
    "/support-plan/{student_code}"
)
def student_support_plan(

    student_code: str,

    db: Session = Depends(
        get_db
    ),
):

    try:

        return build_support_plan(
            db=db,
            student_code=
                student_code,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc