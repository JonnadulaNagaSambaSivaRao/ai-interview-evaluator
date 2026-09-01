from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router

app = FastAPI(
    title="AI Interview Evaluator API",
)

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "AI Interview Evaluator API is running"
    }