from utilities.keyword_match import final_ats_score, experience_level_penalty
from utilities.skills import (
    find_missing_skills,
    calculate_skill_overlap,
    extract_resume_skills,
    extract_required_skills_from_jd,
    clean_text,
)
from services.feedback import generate_resume_feedback


# ---------------------------------------------------------------------------
# Gap analysis
# ---------------------------------------------------------------------------

def extract_gaps(resume_text: str, jd_text: str) -> dict:
    """
    Builds a structured gap report used both for the LLM feedback prompt
    and for any structured API response fields you add later.

    Fields
    ------
    missing_keywords        Top-10 skills in JD that are absent from resume.
    skill_overlap_pct       % of JD skills present in resume.
    matched_skills          Skills the candidate already has that JD wants.
    high_priority_missing   Missing skills that appear more than once in JD
                            (JD emphasises them → higher impact gaps).
    seniority_penalty       Penalty points from experience-level mismatch.
    """
    missing          = find_missing_skills(resume_text, jd_text)
    overlap          = calculate_skill_overlap(resume_text, jd_text)
    resume_skills    = extract_resume_skills(resume_text)
    jd_skills_freq   = extract_required_skills_from_jd(jd_text)

    matched = sorted(resume_skills & set(jd_skills_freq.keys()))

    # Skills the JD mentions more than once — candidate should prioritise these
    high_priority_missing = [
        skill for skill in missing
        if jd_skills_freq.get(skill, 0) > 1
    ]

    penalty = experience_level_penalty(resume_text, jd_text)

    return {
        "missing_keywords":       missing[:10],
        "skill_overlap_percentage": overlap,
        "matched_skills":         matched,
        "high_priority_missing":  high_priority_missing[:5],
        "seniority_penalty":      penalty,
    }


# ---------------------------------------------------------------------------
# Main scoring entry point
# ---------------------------------------------------------------------------

def resume_score(resume_text: str, jd_text: str) -> dict:
    """
    Orchestrates scoring → gap analysis → LLM feedback.

    Returns a dict matching ScoreResponse schema plus a 'summary' field.
    """
    resume_clean = clean_text(resume_text)
    jd_clean     = clean_text(jd_text)

    scores = final_ats_score(resume_clean, jd_clean)
    gaps   = extract_gaps(resume_clean, jd_clean)

    feedback = generate_resume_feedback(scores, gaps)

    return {
        **scores,
        "summary": feedback,
    }