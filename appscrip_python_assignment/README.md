# Trade Opportunities API

A FastAPI-based backend service that analyzes Indian market sectors and returns **structured markdown trade opportunity reports** using:

- Live(ish) web data (DuckDuckGo HTML search with graceful fallback)  
- Google Gemini (LLM) for analysis  
- JWT authentication  
- Per-user rate limiting  
- In-memory session tracking (no database)  

---

## Quick Start

### Installation

```bash
git clone https://github.com/dpkgupta/trade-opportunities-api.git
cd trade-opportunities

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# bash:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file with the following variables:

```
GEMINI_API_KEY=gemini_api_key

JWT_SECRET=some_long_random_secret_value
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

RATE_LIMIT_REQUESTS=3
RATE_LIMIT_WINDOW_SECONDS=60
```

### Running the Application

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

---

## Usage

### Step 1: Get JWT Token

Example users (you can adjust if needed):
- username - prabal / password - prabal123
- username - guest / password - guest123

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=prabal&password=prabal123"
```

**Response:**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### Step 2: Analyze a Sector

**Request:**
```bash
curl "http://127.0.0.1:8000/analyze/pharmaceuticals" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**
```json
{
  "sector": "pharmaceuticals",
  "markdown_report": "# Trade Opportunities Report — Pharmaceuticals (India)\n\n_Generated at: 2025-11-19 17:21 UTC_\n\n## 1. Executive Summary\n..."
}
```

---

## Features

### Main Endpoint

**Single main endpoint**:  
`GET /analyze/{sector}`  
Example: `/analyze/pharmaceuticals`, `/analyze/technology`, `/analyze/agriculture`

### Response Format

A JSON object with:
- `sector`: normalized sector name  
- `markdown_report`: a **ready-to-save `.md` report** containing:
  - Executive summary  
  - Trade opportunities  
  - Risks & watchpoints  
  - Suggested time horizon  
  - Evidence & web source snippets  

### Security

- JWT-based auth (`/token` using OAuth2 password flow)
- Input validation on sector
- Per-user **token-bucket rate limiting** (configurable via env)
- Simple in-memory session tracking (`calls`, timestamps)

---

## Architecture

### Tech Stack

- **Backend**: FastAPI
- **HTTP client**: httpx (async)
- **Auth**: OAuth2 + JWT (`python-jose`, `passlib[bcrypt]`)
- **LLM**: Google Gemini (`google-generativeai`)
- **Parsing**: BeautifulSoup + lxml
- **Storage**: In-memory only (dicts)

### Project Structure

```bash
trade-opportunities/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py               # shared dependencies (auth + rate limit + session)
│   │   └── routes_analyze.py     # /analyze/{sector} endpoint
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── rate_limiter.py       # per-user token-bucket limiter
│   │   ├── security.py           # JWT, OAuth2, user store
│   │   └── session.py            # in-memory session tracking
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_client.py          # Gemini integration
│   │   ├── collector.py          # DuckDuckGo search + parsing
│   │   └── report_builder.py     # Markdown report generator
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analyze.py            # CollectedData, AIAnalysis, AnalyzeResponse
│   │   └── auth.py               # Token, User, UserInDB
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── text.py               # (reserved for small helpers)
│   │
│   ├── config.py                 # Settings (env-based)
│   └── main.py                   # FastAPI app, /token, /health
│
├── .env.example                  # local environment variables 
├── requirements.txt
└── README.md
```
