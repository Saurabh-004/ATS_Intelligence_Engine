import re
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from utilities.skills import (
    extract_resume_skills,
    extract_required_skills_from_jd,
    SKILLS_SORTED_BY_LENGTH,
    clean_text,
)

model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------------------------
# Stop-word list — common English words that pollute keyword matching
# ---------------------------------------------------------------------------
STOP_WORDS: set = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "that", "this", "these", "those", "it", "its", "we", "our", "you",
    "your", "they", "their", "he", "she", "his", "her", "i", "my",
    "not", "no", "so", "if", "then", "than", "also", "just", "only",
    "about", "up", "out", "over", "into", "through", "during", "including",
    "used", "use", "using", "work", "working", "works", "strong", "good",
    "experience", "experiences", "role", "team", "company", "environment",
    "ability", "skills", "skill", "looking", "required", "requirement",
    "plus", "bonus", "nice", "preferred", "knowledge", "understanding",
    "familiarity", "proficiency", "proficient", "hands", "on",
}


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def extract_skill_sentences(text: str) -> str:
    """
    Keep only sentences / bullet points that contain at least one
    known tech skill. Falls back to the full text if nothing matches
    (prevents a zero-length embedding).
    """
    segments = re.split(r'[.\n;]', text)
    cleaned_text = clean_text(text)
    relevant = []
    for seg in segments:
        seg_clean = clean_text(seg)
        if any(skill in seg_clean for skill in SKILLS_SORTED_BY_LENGTH):
            relevant.append(seg_clean)
    return " ".join(relevant) if relevant else cleaned_text


def remove_stop_words(text: str) -> set:
    """Return meaningful tokens after removing stop words."""
    tokens = set(text.split())
    return tokens - STOP_WORDS


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def keyword_match_score(resume_text: str, jd_text: str) -> float:
    """
    Skill-only keyword match.

    Strategy:
    - Extract recognised tech skills from both texts using the master taxonomy.
    - Score = |resume_skills ∩ jd_skills| / |jd_skills|
    - This eliminates stop-word noise and counts only meaningful tech terms.

    Weighting bonus:
    - JD skills that appear multiple times are treated as high-priority.
      A missing high-frequency skill is penalised more heavily.
    """
    jd_skills_freq  = extract_required_skills_from_jd(jd_text)   # {skill: freq}
    resume_skills   = extract_resume_skills(resume_text)

    if not jd_skills_freq:
        return 0.0

    # Weighted scoring: skills mentioned more in JD carry more weight
    total_weight   = sum(jd_skills_freq.values())
    matched_weight = sum(
        freq for skill, freq in jd_skills_freq.items()
        if skill in resume_skills
    )

    return round(matched_weight / total_weight * 100, 2)


def semantic_match_score(resume_text: str, jd_text: str) -> float:
    """
    Skill-focused semantic similarity.

    Strategy:
    - Filter both texts down to skill-relevant sentences before encoding.
    - This focuses the embedding on technical content and reduces noise
      from generic filler language ("we are a fast-paced team...").
    """
    resume_focused = extract_skill_sentences(resume_text)
    jd_focused     = extract_skill_sentences(jd_text)

    embeddings = model.encode([resume_focused, jd_focused])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 2)


def experience_level_penalty(resume_text: str, jd_text: str) -> float:
    """
    Detects seniority mismatch and returns a 0–10 penalty.

    E.g. a senior-level JD matched against a junior resume
    should score lower even if skills overlap.
    """
    SENIOR_SIGNALS = {"senior", "lead", "principal", "architect", "staff", "head of"}
    JUNIOR_SIGNALS = {"junior", "entry level", "entry-level", "graduate", "intern", "fresher"}

    jd_lower     = jd_text.lower()
    resume_lower = resume_text.lower()

    jd_is_senior = any(s in jd_lower for s in SENIOR_SIGNALS)
    jd_is_junior = any(s in jd_lower for s in JUNIOR_SIGNALS)

    resume_is_senior = any(s in resume_lower for s in SENIOR_SIGNALS)
    resume_is_junior = any(s in resume_lower for s in JUNIOR_SIGNALS)

    # JD wants senior but resume signals junior
    if jd_is_senior and resume_is_junior:
        return 10.0
    # JD wants junior but resume is over-qualified (minor penalty)
    if jd_is_junior and resume_is_senior:
        return 3.0
    return 0.0


# ---------------------------------------------------------------------------
# Final composite score
# ---------------------------------------------------------------------------

def final_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Composite ATS score weighted as:
      60%  semantic similarity  (contextual understanding)
      40%  keyword match        (skill taxonomy match, frequency-weighted)

    A seniority mismatch penalty (0–10 pts) is subtracted from the final score.

    Returns a dict compatible with ScoreResponse schema.
    """
    semantic = semantic_match_score(resume_text, jd_text)
    keyword  = keyword_match_score(resume_text, jd_text)
    penalty  = experience_level_penalty(resume_text, jd_text)

    raw_score  = round(0.6 * semantic + 0.4 * keyword, 2)
    final      = round(max(0.0, raw_score - penalty), 2)

    return {
        "semantic_score":  round(semantic, 2),
        "keyword_score":   round(keyword, 2),
        "final_ats_score": final,
    }


# ---------------------------------------------------------------------------
# Smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    examples = [
        [
            "Python developer with FastAPI, SQL, and machine learning experience",
            "Looking for a Python developer with FastAPI, SQL, and ML skills",
        ],
        [
            "Built backend services using Python frameworks and databases",
            "Python developer with FastAPI and SQL",
        ],
        [
            "Python Python Python SQL SQL FastAPI",
            "Python developer with FastAPI and SQL",
        ],
        [
            "Professional photographer specialising in portraits and wildlife",
            "Hiring a machine learning engineer with Python and PyTorch",
        ],
        [
            "Led ML teams, deployed large-scale models, optimised transformers",
            "Junior Python developer with basic ML",
        ],
        [
            "NLP engineer: PyTorch, HuggingFace transformers, LLM fine-tuning, RAG pipelines",
            "Senior ML engineer: LLM, RAG, fine-tuning, Python, AWS SageMaker",
        ],
    ]

    print(f"{'#':<3} {'Semantic':>10} {'Keyword':>10} {'Final ATS':>10}")
    print("-" * 38)
    for i, (resume, jd) in enumerate(examples):
        result = final_ats_score(resume, jd)
        print(
            f"{i:<3} {result['semantic_score']:>10} "
            f"{result['keyword_score']:>10} "
            f"{result['final_ats_score']:>10}"
        )