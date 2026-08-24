import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


class GuardianUpsertRequest(BaseModel):

    guardian_name: str

    relationship: Optional[str] = None

    phone_number: str

    whatsapp_opt_in: bool = False


    @field_validator(
        "phone_number"
    )
    @classmethod
    def normalize_phone(
        cls,
        value: str,
    ) -> str:

        digits = re.sub(
            r"\D",
            "",
            value,
        )

        if not 8 <= len(digits) <= 15:
            raise ValueError(
                "Phone number must include "
                "country code and contain "
                "8 to 15 digits."
            )

        return digits


class GuardianResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    guardian_id: UUID

    student_id: UUID

    guardian_name: str

    relationship: Optional[str]

    phone_number: str

    whatsapp_opt_in: bool

    is_primary: bool


class ParentReportSendResponse(
    BaseModel
):

    report_id: UUID

    student_code: str

    guardian_name: str

    phone_number: str

    support_level: str

    status: str

    whatsapp_message_id: Optional[str]

    sent_at: Optional[datetime]