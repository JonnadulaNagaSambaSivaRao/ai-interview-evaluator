from datetime import datetime

from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

from pydantic import BaseModel, EmailStr

from sqlalchemy.orm import Session

from app.database import get_db, init_db

from app.models.user import User
from app.models.job_role import JobRole
from app.models.interview import Interview
from app.models.interview_question import InterviewQuestion
from app.models.interview_eligibility import InterviewEligibility
from app.models.evaluation_criteria import EvaluationCriteria
from app.models.evaluation import Evaluation
from app.models.final_report import FinalReport

from app.routers.auth import (
    router as auth_router,
    get_current_user,
    get_current_admin,
    get_current_candidate
)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Interview Evaluator API",
    description="Backend API for AI-powered interview evaluation",
    version="1.0.0"
)


app.include_router(auth_router)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

@app.on_event("startup")
def startup():

    init_db()


# =========================================================
# USERS
# =========================================================

class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str
    resume_url: str | None = None


# =========================================================
# CREATE USER
# ADMIN ONLY
# =========================================================

@app.post("/users")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    from app.routers.auth import hash_password

    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="candidate",
        resume_url=data.resume_url
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================================================
# GET USERS
# ADMIN ONLY
# =========================================================

@app.get("/users")
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    return db.query(User).all()


# =========================================================
# GET USER
# ADMIN OR OWN CANDIDATE
# =========================================================

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if (
        current_user.role != "admin"
        and current_user.id != user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="You can only access your own profile"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================================================
# JOB ROLES
# =========================================================

class JobRoleCreate(BaseModel):

    title: str
    description: str | None = None
    required_skills: list[str] = []
    min_experience: int = 0


# =========================================================
# CREATE JOB ROLE
# ADMIN ONLY
# =========================================================

@app.post("/job-roles")
def create_job_role(
    data: JobRoleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    job_role = JobRole(
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        min_experience=data.min_experience
    )

    db.add(job_role)
    db.commit()
    db.refresh(job_role)

    return job_role


# =========================================================
# GET JOB ROLES
# ADMIN + CANDIDATE
# =========================================================

@app.get("/job-roles")
def get_job_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(JobRole).all()


# =========================================================
# GET JOB ROLE
# ADMIN + CANDIDATE
# =========================================================

@app.get("/job-roles/{job_role_id}")
def get_job_role(
    job_role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job_role = (
        db.query(JobRole)
        .filter(JobRole.id == job_role_id)
        .first()
    )

    if not job_role:

        raise HTTPException(
            status_code=404,
            detail="Job role not found"
        )

    return job_role


# =========================================================
# INTERVIEWS
# =========================================================

class InterviewCreate(BaseModel):

    user_id: int
    job_role_id: int


# =========================================================
# CREATE INTERVIEW
# ADMIN ONLY
# =========================================================

@app.post("/interviews")
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    user = (
        db.query(User)
        .filter(User.id == data.user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    job_role = (
        db.query(JobRole)
        .filter(JobRole.id == data.job_role_id)
        .first()
    )

    if not job_role:

        raise HTTPException(
            status_code=404,
            detail="Job role not found"
        )

    interview = Interview(
        user_id=data.user_id,
        job_role_id=data.job_role_id,
        status="scheduled"
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return interview


# =========================================================
# GET ALL INTERVIEWS
# ADMIN ONLY
# =========================================================

@app.get("/interviews")
def get_interviews(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    return db.query(Interview).all()


# =========================================================
# GET SINGLE INTERVIEW
# ADMIN OR OWNER
# =========================================================

@app.get("/interviews/{interview_id}")
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if (
        current_user.role != "admin"
        and interview.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="You cannot access this interview"
        )

    return interview


# =========================================================
# START INTERVIEW
# CANDIDATE OWNER
# =========================================================

@app.patch("/interviews/{interview_id}/start")
def start_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(get_current_candidate)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if interview.user_id != candidate.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot start this interview"
        )

    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()

    db.commit()
    db.refresh(interview)

    return interview


# =========================================================
# COMPLETE INTERVIEW
# CANDIDATE OWNER
# =========================================================

@app.patch("/interviews/{interview_id}/complete")
def complete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(get_current_candidate)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if interview.user_id != candidate.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot complete this interview"
        )

    interview.status = "completed"
    interview.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(interview)

    return interview


# =========================================================
# INTERVIEW QUESTIONS
# =========================================================

class QuestionCreate(BaseModel):

    interview_id: int
    question_text: str
    question_type: str = "technical"
    order_no: int


# =========================================================
# CREATE QUESTION
# ADMIN ONLY
# =========================================================

@app.post("/questions")
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == data.interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    question = InterviewQuestion(
        interview_id=data.interview_id,
        question_text=data.question_text,
        question_type=data.question_type,
        order_no=data.order_no
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


# =========================================================
# GET QUESTIONS
# ADMIN OR INTERVIEW OWNER
# =========================================================

@app.get("/interviews/{interview_id}/questions")
def get_questions(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if (
        current_user.role != "admin"
        and interview.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="You cannot access these questions"
        )

    return (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id == interview_id
        )
        .order_by(
            InterviewQuestion.order_no
        )
        .all()
    )


# =========================================================
# ANSWER
# CANDIDATE
# =========================================================

class AnswerSubmit(BaseModel):

    answer: str


@app.patch("/questions/{question_id}/answer")
def submit_answer(
    question_id: int,
    data: AnswerSubmit,
    db: Session = Depends(get_db),
    candidate: User = Depends(get_current_candidate)
):

    question = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.id == question_id
        )
        .first()
    )

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == question.interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if interview.user_id != candidate.id:

        raise HTTPException(
            status_code=403,
            detail="You cannot answer this question"
        )

    question.answer = data.answer

    db.commit()
    db.refresh(question)

    return question


# =========================================================
# ELIGIBILITY
# =========================================================

class EligibilityCreate(BaseModel):

    interview_id: int
    eligible: bool
    score: float
    reason: str


# =========================================================
# CREATE ELIGIBILITY
# ADMIN ONLY
# =========================================================

@app.post("/eligibility")
def create_eligibility(
    data: EligibilityCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == data.interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    eligibility = InterviewEligibility(
        interview_id=data.interview_id,
        eligible=data.eligible,
        score=data.score,
        reason=data.reason
    )

    db.add(eligibility)
    db.commit()
    db.refresh(eligibility)

    return eligibility


# =========================================================
# GET ELIGIBILITY
# ADMIN OR OWNER
# =========================================================

@app.get("/interviews/{interview_id}/eligibility")
def get_eligibility(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interview = (
        db.query(Interview)
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if (
        current_user.role != "admin"
        and interview.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    result = (
        db.query(InterviewEligibility)
        .filter(
            InterviewEligibility.interview_id
            == interview_id
        )
        .first()
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="Eligibility result not found"
        )

    return result


# =========================================================
# EVALUATION CRITERIA
# =========================================================

class CriteriaCreate(BaseModel):

    name: str
    description: str | None = None
    weight: float = 1.0


# =========================================================
# CREATE CRITERIA
# ADMIN
# =========================================================

@app.post("/evaluation-criteria")
def create_criteria(
    data: CriteriaCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    criteria = EvaluationCriteria(
        name=data.name,
        description=data.description,
        weight=data.weight
    )

    db.add(criteria)
    db.commit()
    db.refresh(criteria)

    return criteria


# =========================================================
# GET CRITERIA
# ADMIN + CANDIDATE
# =========================================================

@app.get("/evaluation-criteria")
def get_criteria(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(
        EvaluationCriteria
    ).all()


# =========================================================
# EVALUATION
# =========================================================

class EvaluationCreate(BaseModel):

    interview_id: int
    question_id: int | None = None
    criteria_scores: dict
    overall_score: float
    feedback: str


# =========================================================
# CREATE EVALUATION
# ADMIN ONLY
# =========================================================

@app.post("/evaluations")
def create_evaluation(
    data: EvaluationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == data.interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    evaluation = Evaluation(
        interview_id=data.interview_id,
        question_id=data.question_id,
        criteria_scores=data.criteria_scores,
        overall_score=data.overall_score,
        feedback=data.feedback
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation


# =========================================================
# GET EVALUATIONS
# ADMIN OR OWNER
# =========================================================

@app.get("/interviews/{interview_id}/evaluations")
def get_evaluations(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if (
        current_user.role != "admin"
        and interview.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return (
        db.query(Evaluation)
        .filter(
            Evaluation.interview_id == interview_id
        )
        .all()
    )


# =========================================================
# FINAL REPORT
# =========================================================

class FinalReportCreate(BaseModel):

    interview_id: int
    overall_score: float
    recommendation: str
    summary: str
    strengths: list[str]
    weaknesses: list[str]


# =========================================================
# CREATE FINAL REPORT
# ADMIN ONLY
# =========================================================

@app.post("/final-reports")
def create_final_report(
    data: FinalReportCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == data.interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    report = FinalReport(
        interview_id=data.interview_id,
        overall_score=data.overall_score,
        recommendation=data.recommendation,
        summary=data.summary,
        strengths=data.strengths,
        weaknesses=data.weaknesses
    )

    interview.score = data.overall_score

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# =========================================================
# GET FINAL REPORT
# ADMIN OR OWNER
# =========================================================

@app.get("/interviews/{interview_id}/final-report")
def get_final_report(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id
        )
        .first()
    )

    if not interview:

        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    if (
        current_user.role != "admin"
        and interview.user_id != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    report = (
        db.query(FinalReport)
        .filter(
            FinalReport.interview_id == interview_id
        )
        .first()
    )

    if not report:

        raise HTTPException(
            status_code=404,
            detail="Final report not found"
        )

    return report