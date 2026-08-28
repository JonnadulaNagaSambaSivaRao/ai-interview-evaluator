from fastapi import FastAPI

from app.database import Base, engine

# Import all models
from app.models import (
    User,
    JobRole,
    Interview,
    InterviewQuestion,
    InterviewEligibility,
    InterviewAttempt,
    Evaluation,
    FinalReport
)

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.candidate import router as candidate_router


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="AI Interview Evaluator API",
    version="1.0.0"
)


app.include_router(
    auth_router
)

app.include_router(
    admin_router
)

app.include_router(
    candidate_router
)


@app.get("/")
def root():

    return {
        "message": "AI Interview Evaluator API is running"
    }