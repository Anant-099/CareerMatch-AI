# CareerMatch AI

# CareerMatch AI

### 🚀 [**LIVE DEMO — Try CareerMatch AI Here**](https://career-match-ai-bay.vercel.app/)

AI-powered resume and job description matching platform that helps users analyze skills, identify gaps, and get AI-generated resume feedback.

**[🌐 Open Application](https://career-match-ai-bay.vercel.app/)** | **[📂 View Source Code](https://github.com/Anant-099/CareerMatch-AI)**

**AI-Powered Resume and Job Description Matching Platform**

CareerMatch AI is a web application that analyzes a resume against a job description, calculates a skill-based match score, identifies matching and missing skills, and provides recommendations to help users improve their resumes.

## Features

- **PDF Resume Upload:** Upload a resume in PDF format for analysis.
- **Job Description Analysis:** Extract relevant skills from a job description.
- **Match Score:** Calculate a weighted skill coverage score.
- **Skill Gap Analysis:** Identify matched and missing skills.
- **Skill Breakdown:** Organize skills into categories.
- **Personalized Recommendations:** Suggest ways to improve missing skills, including project ideas.
- **Analysis History:** Save and retrieve previous analyses using PostgreSQL.
- **REST API:** Access backend functionality through FastAPI and Swagger UI.

## Tech Stack

- **Frontend:** React, Vite, JavaScript
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **PDF Processing:** pypdf
- **Testing:** pytest, unittest, FastAPI TestClient

## Project Structure

```text
Career Match AI/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── init_db.py
│   ├── requirements.txt
│   ├── test_api.py
│   ├── test_main.py
│   └── test_db_connection.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Prerequisites

- Python
- Node.js and npm
- PostgreSQL

## Backend Setup

Open a terminal in the project root.

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment in Git Bash:

```bash
source .venv/Scripts/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Create a `backend/.env` file with your local PostgreSQL configuration:

```dotenv
DB_USER=postgres
DB_PASSWORD=your_local_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=careermatch_ai
```

Replace the example password with your own local database password. Never commit `.env` to GitHub.

Create the database `careermatch_ai` in PostgreSQL if it does not already exist, then initialize the tables:

```bash
python init_db.py
```

Start the backend server:

```bash
python -m uvicorn main:app --reload
```

### Backend URLs

- API documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/api/health

## Frontend Setup

Open a second terminal in the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in the terminal.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check backend health |
| POST | `/api/analyze` | Analyze a resume against a job description |
| GET | `/api/history` | Retrieve saved analysis history |

Use Swagger UI at `/docs` to inspect and test the API endpoints.

## Run Tests

From the project root:

```bash
cd backend
python -m pytest -q
```

The current test suite has **17 passing tests** in the development environment.

## Future Improvements

- Isolated automated test database
- User accounts and authentication
- Improved semantic matching using embeddings
- Interview question generation
- Deployment to a public hosting platform

## Project Status

The resume analysis platform, skill gap analysis, recommendations, PostgreSQL persistence, and analysis history interface have been implemented and tested locally. The frontend build and core features have been verified. Production deployment and final release preparation are the remaining steps.

---

*CareerMatch AI — helping job seekers understand how their skills align with job requirements.*
