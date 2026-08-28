from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import get_current_admin

from app.models.user import User
from app.models.job_role import JobRole
from app.models.interview import Interview
from app.models.interview_question import InterviewQuestion
from app.models.interview_eligibility import InterviewEligibility
from app.models.interview_attempt import InterviewAttempt
from app.models.evaluation import Evaluation
from app.models.final_report import FinalReport

from app.schemas.question import QuestionCreate


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================
# DASHBOARD
# =========================

@router.get("/dashboard")
def dashboard(
    admin: User = Depends(get_current_admin)
):

    return {
        "message": "Welcome Admin",
        "user": admin.email,
        "role": admin.role
    }


# =========================
# USERS
# =========================

@router.get("/users")
def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(User).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)

    db.commit()

    return {
        "message": "User deleted successfully"
    }


# =========================
# JOB ROLES
# =========================

@router.post("/job-roles")
def create_job_role(
    name: str,
    description: str = "",

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    existing = db.query(JobRole).filter(
        JobRole.name == name
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Job role already exists"
        )

    role = JobRole(
        name=name,
        description=description
    )

    db.add(role)

    db.commit()

    db.refresh(role)

    return role


@router.get("/job-roles")
def get_job_roles(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(JobRole).all()


# =========================
# INTERVIEWS
# =========================

@router.get("/interviews")
def get_all_interviews(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(Interview).all()


@router.post("/interviews")
def create_interview(
    title: str,
    description: str = "",
    job_role_id: int | None = None,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    interview = Interview(
        title=title,
        description=description,
        job_role_id=job_role_id,
        status="active"
    )

    db.add(interview)

    db.commit()

    db.refresh(interview)

    return interview


@router.put("/interviews/{interview_id}")
def update_interview(
    interview_id: int,
    title: str,
    description: str = "",

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    interview = db.query(
        Interview
    ).filter(
        Interview.id == interview_id
    ).first()

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    interview.title = title
    interview.description = description

    db.commit()

    db.refresh(interview)

    return interview


@router.delete("/interviews/{interview_id}")
def delete_interview(
    interview_id: int,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    interview = db.query(
        Interview
    ).filter(
        Interview.id == interview_id
    ).first()

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    db.delete(interview)

    db.commit()

    return {
        "message": "Interview deleted successfully"
    }


# =========================
# QUESTIONS
# =========================

@router.post(
    "/interviews/{interview_id}/questions"
)
def create_question(
    interview_id: int,

    data: QuestionCreate,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    interview = db.query(
        Interview
    ).filter(
        Interview.id == interview_id
    ).first()

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    # Question template.
    # attempt_id is 0 until copied to an attempt.
    question = InterviewQuestion(
        interview_id=interview_id,
        attempt_id=0,
        question=data.question,
        question_type=data.question_type,
        marks=data.marks
    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return question


@router.get(
    "/interviews/{interview_id}/questions"
)
def get_questions(
    interview_id: int,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    return db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.interview_id == interview_id
    ).all()


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    question = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.id == question_id
    ).first()

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    db.delete(question)

    db.commit()

    return {
        "message": "Question deleted successfully"
    }


# =========================
# ASSIGN CANDIDATE
# =========================

@router.post(
    "/interviews/{interview_id}/assign/{candidate_id}"
)
def assign_candidate(
    interview_id: int,
    candidate_id: int,

    admin: User = Depends(get_current_admin),

    db: Session = Depends(get_db)
):

    candidate = db.query(User).filter(
        User.id == candidate_id,
        User.role == "candidate"
    ).first()

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    interview = db.query(
        Interview
    ).filter(
        Interview.id == interview_id
    ).first()

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    existing = db.query(
        InterviewEligibility
    ).filter(
        InterviewEligibility.candidate_id
        == candidate_id,

        InterviewEligibility.interview_id
        == interview_id
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Candidate already assigned"
        )

    eligibility = InterviewEligibility(
        candidate_id=candidate_id,
        interview_id=interview_id,
        status="assigned"
    )

    db.add(eligibility)

    db.commit()

    return {
        "message": "Candidate assigned successfully"
    }


# =========================
# ALL ATTEMPTS
# =========================

@router.get("/attempts")
def get_all_attempts(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(
        InterviewAttempt
    ).all()


# =========================
# ALL RESULTS
# =========================

@router.get("/results")
def get_all_results(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.status == "completed"
    ).all()


# =========================
# ALL HISTORY
# =========================

@router.get("/history")
def get_all_history(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(
        InterviewAttempt
    ).order_by(
        InterviewAttempt.started_at.desc()
    ).all()


# =========================
# ALL EVALUATIONS
# =========================

@router.get("/evaluations")
def get_all_evaluations(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(
        Evaluation
    ).all()


# =========================
# ALL FINAL REPORTS
# =========================

@router.get("/reports")
def get_all_reports(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):

    return db.query(
        FinalReport
    ).all()