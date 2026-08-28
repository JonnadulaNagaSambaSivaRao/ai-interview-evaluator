from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import get_current_candidate

from app.models.user import User
from app.models.interview import Interview
from app.models.interview_question import InterviewQuestion
from app.models.interview_eligibility import InterviewEligibility
from app.models.interview_attempt import InterviewAttempt

from app.schemas.question import AnswerSubmit


router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"]
)


# =========================
# DASHBOARD
# =========================

@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(
        get_current_candidate
    )
):

    return {
        "message": "Candidate Dashboard",
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


# =========================
# MY INTERVIEWS
# =========================

@router.get("/interviews")
def my_interviews(
    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    interviews = (
        db.query(Interview)
        .join(
            InterviewEligibility,
            InterviewEligibility.interview_id
            == Interview.id
        )
        .filter(
            InterviewEligibility.candidate_id
            == current_user.id
        )
        .all()
    )

    return interviews


# =========================
# START INTERVIEW
# =========================

@router.post(
    "/interviews/{interview_id}/start"
)
def start_interview(
    interview_id: int,

    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    # Check assignment
    eligibility = db.query(
        InterviewEligibility
    ).filter(
        InterviewEligibility.candidate_id
        == current_user.id,

        InterviewEligibility.interview_id
        == interview_id
    ).first()

    if not eligibility:

        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this interview"
        )

    # Check interview
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

    # Check existing active attempt
    existing_attempt = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.interview_id
        == interview_id,

        InterviewAttempt.status
        == "started"
    ).first()

    if existing_attempt:

        return {
            "message": "Interview already started",
            "attempt_id": existing_attempt.id
        }

    # Create attempt
    attempt = InterviewAttempt(
        candidate_id=current_user.id,
        interview_id=interview_id,
        status="started"
    )

    db.add(attempt)

    db.flush()

    # Get admin question templates
    templates = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.interview_id
        == interview_id,

        InterviewQuestion.attempt_id.is_(None)
    ).all()

    # Create candidate-specific
    # question/answer rows
    for template in templates:

        candidate_question = InterviewQuestion(
            interview_id=interview_id,
            attempt_id=attempt.id,
            question=template.question,
            question_type=template.question_type,
            marks=template.marks
        )

        db.add(candidate_question)

    db.commit()

    db.refresh(attempt)

    return {
        "message": "Interview started",
        "attempt_id": attempt.id,
        "interview_id": interview_id
    }


# =========================
# GET QUESTIONS
# =========================

@router.get(
    "/interviews/{interview_id}/questions"
)
def get_questions(
    interview_id: int,

    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    attempt = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.interview_id
        == interview_id,

        InterviewAttempt.status
        == "started"
    ).first()

    if not attempt:

        raise HTTPException(
            status_code=403,
            detail="No active interview found"
        )

    questions = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.attempt_id
        == attempt.id
    ).all()

    return questions


# =========================
# SUBMIT ANSWER
# =========================

@router.post(
    "/interviews/{interview_id}/answers"
)
def submit_answer(
    interview_id: int,

    data: AnswerSubmit,

    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    # Find candidate's attempt
    attempt = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.interview_id
        == interview_id,

        InterviewAttempt.status
        == "started"
    ).first()

    if not attempt:

        raise HTTPException(
            status_code=403,
            detail="No active interview attempt"
        )

    # Find question belonging to
    # THIS candidate's attempt
    question = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.id
        == data.question_id,

        InterviewQuestion.attempt_id
        == attempt.id
    ).first()

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # Save answer
    question.answer = data.answer

    db.commit()

    return {
        "message": "Answer saved successfully",
        "question_id": question.id
    }


# =========================
# SUBMIT INTERVIEW
# =========================

@router.post(
    "/interviews/{interview_id}/submit"
)
def submit_interview(
    interview_id: int,

    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    attempt = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.interview_id
        == interview_id,

        InterviewAttempt.status
        == "started"
    ).first()

    if not attempt:

        raise HTTPException(
            status_code=404,
            detail="Active interview not found"
        )

    attempt.status = "completed"

    attempt.submitted_at = datetime.utcnow()

    # Calculate simple score
    questions = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.attempt_id
        == attempt.id
    ).all()

    total_score = 0

    for question in questions:

        if question.score is not None:

            total_score += question.score

    attempt.score = total_score

    db.commit()

    return {
        "message": "Interview submitted successfully",
        "attempt_id": attempt.id,
        "score": total_score
    }


# =========================
# MY RESULTS
# =========================

@router.get("/results")
def my_results(
    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    results = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.status
        == "completed"
    ).all()

    return results


# =========================
# MY HISTORY
# =========================

@router.get("/history")
def my_history(
    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    history = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id
    ).order_by(
        InterviewAttempt.started_at.desc()
    ).all()

    return history


# =========================
# MY ANSWERS
# =========================

@router.get(
    "/interviews/{interview_id}/answers"
)
def my_answers(
    interview_id: int,

    current_user: User = Depends(
        get_current_candidate
    ),

    db: Session = Depends(get_db)
):

    attempt = db.query(
        InterviewAttempt
    ).filter(
        InterviewAttempt.candidate_id
        == current_user.id,

        InterviewAttempt.interview_id
        == interview_id
    ).order_by(
        InterviewAttempt.started_at.desc()
    ).first()

    if not attempt:

        raise HTTPException(
            status_code=404,
            detail="Interview attempt not found"
        )

    questions = db.query(
        InterviewQuestion
    ).filter(
        InterviewQuestion.attempt_id
        == attempt.id
    ).all()

    return questions