from pydantic import BaseModel


class QuestionCreate(BaseModel):
    question: str
    question_type: str = "text"
    marks: int = 10


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str