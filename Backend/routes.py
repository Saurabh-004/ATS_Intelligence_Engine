# routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from schemas import ScoreResponse, ScoreRequest
from services.scorer import resume_score
from utilities.pdf_parser import extract_text_from_pdf
from utilities.keyword_match import clean_text

router = APIRouter(prefix="/predict", tags=["Prediction"])


# ── JSON route (both inputs are plain text) ────────────────────────────────
@router.post("/ats", response_model=ScoreResponse)
async def predict_ats_json(payload: ScoreRequest):
    resume_clean = clean_text(payload.resume_text)
    jd_clean     = clean_text(payload.job_description)
    return resume_score(resume_clean, jd_clean)


# ── Multipart route (one or both inputs are PDFs) ─────────────────────────
@router.post("/ats/upload", response_model=ScoreResponse)
async def predict_ats_upload(
    resume_pdf:    Optional[UploadFile] = File(None,  description="Resume PDF (optional)"),
    jd_pdf:        Optional[UploadFile] = File(None,  description="JD PDF (optional)"),
    resume_text:   Optional[str]        = Form(None,  description="Resume plain text (optional)"),
    job_description: Optional[str]      = Form(None,  description="JD plain text (optional)"),
):
    # ── Resolve resume text ──────────────────────────────────────────────
    if resume_pdf and resume_pdf.filename:
        if resume_pdf.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="resume_pdf must be a PDF file.")
        try:
            resume_raw = extract_text_from_pdf(await resume_pdf.read())
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif resume_text:
        resume_raw = resume_text
    else:
        raise HTTPException(status_code=422, detail="Provide either resume_pdf or resume_text.")

    # ── Resolve JD text ──────────────────────────────────────────────────
    if jd_pdf and jd_pdf.filename:
        if jd_pdf.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="jd_pdf must be a PDF file.")
        try:
            jd_raw = extract_text_from_pdf(await jd_pdf.read())
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
    elif job_description:
        jd_raw = job_description
    else:
        raise HTTPException(status_code=422, detail="Provide either jd_pdf or job_description.")

    resume_clean = clean_text(resume_raw)
    jd_clean     = clean_text(jd_raw)
    return resume_score(resume_clean, jd_clean)