from pydantic import BaseModel

class ScoreRequest(BaseModel):
    resume_text: str
    job_description: str

class ScoreResponse(BaseModel):
    semantic_score: float
    keyword_score: float
    final_ats_score: float
    summary: str

