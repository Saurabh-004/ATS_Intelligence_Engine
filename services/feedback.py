from .llm import client

def generate_resume_feedback(scores: dict, gaps: dict) -> str:
    prompt = f"""
You are an ATS resume analyst.

You MUST base your feedback ONLY on:
- The provided ATS scores
- The detected gaps
- The resume content

DO NOT invent missing skills.
DO NOT give generic advice.
DO NOT mention motivation, confidence, or mindset.

ATS Scores:
Semantic: {scores['semantic_score']}
Keyword: {scores['keyword_score']}
Final: {scores['final_ats_score']}

Detected Gaps:
Missing Keywords: {gaps['missing_keywords']}
Skill Overlap: {gaps['skill_overlap_percentage']}%

Task:
Write a concise analysis with exactly 3 sections:

1. Score Explanation  
2. Weak Areas  
3. Actionable Improvements  

Keep it under 500 words.
"""

    response = client.chat.completions.create(
        model="allenai/Olmo-3-7B-Instruct",
        messages=[
            {
                "role": "assistant",
                "content": prompt,
            }
        ],
    )

    if not response or not response.choices:
        return "Feedback generation failed."

    return response.choices[0].message.content.strip()
