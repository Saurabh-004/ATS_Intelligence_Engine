import re

# ---------------------------------------------------------------------------
# Tech Skill Taxonomy
# Multi-word phrases are matched BEFORE single tokens to avoid partial hits.
# Each category is kept separate so it's easy to extend.
# ---------------------------------------------------------------------------

# --- Languages ---
LANGUAGES = {
    "python", "java", "javascript", "typescript", "golang", "go",
    "rust", "ruby", "scala", "kotlin", "swift", "php", "r", "matlab",
    "bash", "shell", "c", "cpp", "c++", "csharp", "c#",
}

# --- Web Frameworks ---
WEB_FRAMEWORKS = {
    "fastapi", "flask", "django", "spring boot", "spring",
    "express", "nestjs", "nextjs", "nuxtjs", "rails",
    "laravel", "fiber", "gin",
}

# --- Frontend ---
FRONTEND = {
    "react", "angular", "vue", "svelte", "html", "css",
    "tailwind", "bootstrap", "redux", "webpack", "vite",
}

# --- APIs & Architecture ---
API_ARCH = {
    "rest api", "restful api", "graphql", "grpc", "websocket",
    "microservices", "microservice", "event driven", "message queue",
    "api gateway", "api",
}

# --- Databases ---
DATABASES = {
    "postgresql", "postgres", "mysql", "sqlite", "oracle",
    "mongodb", "mongo", "redis", "cassandra", "dynamodb",
    "elasticsearch", "neo4j", "firebase", "supabase",
    "sql", "nosql", "vector database", "pinecone", "weaviate",
}

# --- ML / AI / Data Science ---
ML_AI = {
    "machine learning", "deep learning", "reinforcement learning",
    "supervised learning", "unsupervised learning",
    "natural language processing", "nlp", "computer vision",
    "large language model", "llm", "generative ai", "gen ai",
    "transformers", "bert", "gpt", "llama", "mistral",
    "scikit-learn", "scikit learn", "sklearn",
    "pytorch", "torch", "tensorflow", "keras", "jax",
    "hugging face", "huggingface", "langchain", "llamaindex",
    "xgboost", "lightgbm", "catboost",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "mlflow", "mlops", "model serving", "model deployment",
    "feature engineering", "hyperparameter tuning",
    "rag", "retrieval augmented generation", "fine tuning", "fine-tuning",
    "diffusion models", "stable diffusion",
    "data analysis", "data analytics", "data science",
    "statistical analysis", "statistics", "probability",
    "a/b testing", "hypothesis testing",
}

# --- Data Engineering ---
DATA_ENGINEERING = {
    "apache spark", "spark", "hadoop", "kafka", "airflow",
    "dbt", "flink", "hive", "presto", "trino",
    "etl", "elt", "data pipeline", "data warehouse",
    "snowflake", "bigquery", "redshift", "databricks",
}

# --- Cloud & Infrastructure ---
CLOUD = {
    "aws", "amazon web services", "azure", "gcp", "google cloud",
    "ec2", "s3", "lambda", "sagemaker", "bedrock",
    "cloudformation", "terraform", "pulumi",
    "serverless", "cloud functions",
}

# --- DevOps & CI/CD ---
DEVOPS = {
    "docker", "kubernetes", "k8s", "helm",
    "ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins",
    "ansible", "chef", "puppet",
    "linux", "unix", "nginx", "apache",
    "monitoring", "observability", "prometheus", "grafana",
    "opentelemetry", "datadog", "new relic",
}

# --- Version Control & Collaboration ---
VCS = {
    "git", "github", "gitlab", "bitbucket", "version control",
}

# --- System Design & Software Engineering ---
ENGINEERING = {
    "system design", "software design", "object oriented", "oop",
    "design patterns", "solid principles", "clean code",
    "distributed systems", "high availability", "scalability",
    "load balancing", "caching", "message broker",
    "unit testing", "integration testing", "tdd", "bdd",
    "pytest", "junit", "jest", "mocha",
    "code review", "agile", "scrum", "kanban",
}

# --- Security ---
SECURITY = {
    "cybersecurity", "penetration testing", "pen testing",
    "oauth", "jwt", "ssl", "tls", "encryption",
    "owasp", "security auditing",
}

# ---------------------------------------------------------------------------
# Master set — sorted longest-first so multi-word phrases match before tokens
# ---------------------------------------------------------------------------
GENERAL_TECH_SKILLS: set = (
    LANGUAGES | WEB_FRAMEWORKS | FRONTEND | API_ARCH |
    DATABASES | ML_AI | DATA_ENGINEERING | CLOUD |
    DEVOPS | VCS | ENGINEERING | SECURITY
)

# Pre-sorted for greedy multi-word matching (longest phrase wins)
SKILLS_SORTED_BY_LENGTH: list = sorted(GENERAL_TECH_SKILLS, key=len, reverse=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s/]', ' ', text)   # keep / for ci/cd etc.
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_skills(text: str) -> set:
    """
    Greedy left-to-right phrase match.
    Multi-word skills (e.g. 'machine learning') are checked before
    their constituent tokens to prevent double-counting.
    """
    cleaned = clean_text(text)
    found: set = set()
    consumed_positions: set = set()       # char positions already claimed

    for skill in SKILLS_SORTED_BY_LENGTH:
        start = 0
        while True:
            idx = cleaned.find(skill, start)
            if idx == -1:
                break
            end = idx + len(skill)

            # Boundary check — skill must be a whole word / phrase
            before_ok = (idx == 0 or cleaned[idx - 1] == ' ')
            after_ok  = (end == len(cleaned) or cleaned[end] == ' ')

            if before_ok and after_ok:
                span = set(range(idx, end))
                if not span & consumed_positions:   # no overlap with claimed chars
                    found.add(skill)
                    consumed_positions |= span
                    break           # found this skill, move to next

            start = idx + 1

    return found


def extract_required_skills_from_jd(jd_text: str) -> dict:
    """Return JD skills with mention-frequency as an importance signal."""
    skills = extract_skills(jd_text)
    cleaned = clean_text(jd_text)
    return {skill: cleaned.count(skill) for skill in skills}


def extract_resume_skills(resume_text: str) -> set:
    return extract_skills(resume_text)


def find_missing_skills(resume_text: str, jd_text: str) -> list:
    jd_skills   = set(extract_required_skills_from_jd(jd_text).keys())
    resume_skills = extract_resume_skills(resume_text)
    return [s for s in jd_skills if s not in resume_skills]


def calculate_skill_overlap(resume_text: str, jd_text: str) -> float:
    jd_skills     = set(extract_required_skills_from_jd(jd_text).keys())
    resume_skills = extract_resume_skills(resume_text)
    if not jd_skills:
        return 0.0
    return round(len(jd_skills & resume_skills) / len(jd_skills) * 100, 2)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    resume_text = (
        "Python, NumPy, Pandas, Scikit-learn, PyTorch, TensorFlow, spaCy. "
        "Machine Learning, NLP, Feature Engineering, Model Evaluation. "
        "Flask, FastAPI, Git, GitHub, Linux, MLflow, Docker."
    )
    jd_text = (
        "Machine Learning Engineer. Strong Python. Amazon SageMaker. "
        "ML model deployment. APIs. GenAI / LLM solutions. "
        "MLOps: model monitoring, drift detection, retraining. "
        "Data pipelines. CI/CD. Kubernetes."
    )
    clean_r = clean_text(resume_text)
    clean_j = clean_text(jd_text)
    print("Missing skills :", find_missing_skills(clean_r, clean_j))
    print("Skill overlap  :", calculate_skill_overlap(clean_r, clean_j), "%")
    print("Resume skills  :", extract_resume_skills(clean_r))
    print("JD skills      :", set(extract_required_skills_from_jd(clean_j).keys()))