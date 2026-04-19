from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
)

if __name__ == "__main__":
    summarizer = client.chat.completions.create(
        model="allenai/Olmo-3-7B-Instruct",
        messages=[
            {
                "role": "assistant",
                "content": "You MUST base your feedback ONLY on: - The provided ATS scores - The detected gaps - The resume content DO NOT invent missing skills. DO NOT give generic advice. DO NOT mention motivation, confidence, or mindset. ATS Scores: Semantic: {45} Keyword: {70} Final: {68} Detected Gaps: Missing Keywords: {api, tensorflow, docker} Skill Overlap: {70}% Task: Write a concise analysis with exactly 3 sections: 1. Score Explanation Explain why the ATS score is high or low using the scores and gaps. 2. Weak Areas Point out specific missing skills, tools 3. Actionable Improvements Give concrete fixes (e.g., “Add X project”, “Mention Y tool”), no vague advice. Keep it under 500 word"
            }
        ],
    )

    print(summarizer.choices[0].message)