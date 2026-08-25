from pydantic import BaseModel, Field


class SendParentReportRequest(BaseModel):
    guardian_id: str
    mentor_note: str | None = Field(default=None, max_length=1000)
