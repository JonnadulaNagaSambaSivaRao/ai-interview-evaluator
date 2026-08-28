from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================
# CREATE INTERVIEW
# =========================

class InterviewCreate(BaseModel):
    title: str
    description: str | None = None
    job_role_id: int | None = None


# =========================
# UPDATE INTERVIEW
# =========================

class InterviewUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    job_role_id: int | None = None
    status: str | None = None


# =========================
# INTERVIEW RESPONSE
# =========================

class InterviewResponse(BaseModel):
    id: int
    title: str
    description: str | None
    job_role_id: int | None
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================
# ASSIGN INTERVIEW
# =========================

class InterviewAssignRequest(BaseModel):
    candidate_id: int


# =========================
# INTERVIEW ASSIGNMENT RESPONSE
# =========================

class InterviewEligibilityResponse(BaseModel):
    id: int
    candidate_id: int
    interview_id: int
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================
# START INTERVIEW RESPONSE
# =========================

class InterviewStartResponse(BaseModel):
    message: str
    attempt_id: int
    interview_id: int