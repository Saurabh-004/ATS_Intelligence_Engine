# ATS Resume Matcher

An AI-powered Applicant Tracking System that scores resumes against job descriptions using semantic similarity. Built with FastAPI on the backend and served via Nginx, fully containerized with Docker.

---

## Features

- Upload a resume (PDF or plain text) and a job description (PDF or plain text)
- Extracts text from PDFs using PyMuPDF
- Computes **semantic similarity** using Sentence Transformers
- Computes **keyword match score** for direct skill overlap
- Returns a final ATS score with a summary
- REST API built with FastAPI
- Dockerized for easy deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| ML / Embeddings | Sentence Transformers, Scikit-learn |
| PDF Parsing | PyMuPDF |
| Frontend | HTML/JS served via Nginx |
| Containerization | Docker, Docker Compose |
| Model Hub | HuggingFace Hub |

---

## Project Structure
.
├── main.py                  # FastAPI app entry point
├── routes.py                # API route definitions
├── schemas.py               # Pydantic request/response models
├── services/
│   └── scorer.py            # Scoring logic (semantic + keyword)
├── utilities/
│   ├── pdf_parser.py        # PDF text extraction
│   └── keyword_match.py     # Text cleaning and keyword matching
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Multi-service Docker setup
├── Dockerfile               # Backend container definition
├── frontend/                # Static frontend files
└── nginx.conf               # Nginx configuration

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed
- A HuggingFace API token

### 1. Clone the repository

```bash
git clone https://github.com/Saurabh-004/ATS_Intelligence_Engine
cd ats-resume-matcher
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```env
HF_TOKEN=your_huggingface_token_here
```

### 3. Run with Docker Compose

```bash
docker compose up --build
```

- **Backend API** → `http://localhost:8000`
- **Frontend** → `http://localhost:80`

---

## API Endpoints

### `POST /predict/ats` — JSON Input

Both resume and JD as plain text.

**Request body:**
```json
{
  "resume_text": "...",
  "job_description": "..."
}
```

---

### `POST /predict/ats/upload` — Multipart/Form-Data

Accepts PDFs and/or plain text for either input.

| Field | Type | Description |
|---|---|---|
| `resume_pdf` | File (PDF) | Resume as PDF (optional) |
| `resume_text` | string | Resume as plain text (optional) |
| `jd_pdf` | File (PDF) | Job description as PDF (optional) |
| `job_description` | string | Job description as plain text (optional) |

> Provide at least one of `resume_pdf` or `resume_text`, and at least one of `jd_pdf` or `job_description`.

---

### Response (both endpoints)

```json
{
  "semantic_score": 0.82,
  "keyword_score": 0.74,
  "final_ats_score": 0.79,
  "summary": "..."
}
```

---

## How It Works

1. Resume and job description text are extracted (from PDF or raw input)
2. Both texts are cleaned and normalized
3. **Semantic score** — computed via cosine similarity on Sentence Transformer embeddings
4. **Keyword score** — computed via direct keyword overlap between resume and JD
5. A **final ATS score** is derived as a weighted combination of both
6. A human-readable **summary** is returned alongside the scores

---

## Development (without Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | HuggingFace API token for downloading models |

---

## License

MIT License. Feel free to use and modify.