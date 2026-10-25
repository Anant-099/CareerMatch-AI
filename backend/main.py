
from io import BytesIO
import re

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from database import get_db
from models import AnalysisHistory
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

app = FastAPI(title="CareerMatch AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


SKILL_ALIASES = {
    # Programming languages
    "python": ["python", "python3"],
    "java": ["java"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "c": ["c programming", "c language"],
    "c++": ["c++"],
    "c#": ["c#"],
    "go": ["golang", "go language"],
    "rust": ["rust"],
    "php": ["php"],
    "ruby": ["ruby"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "scala": ["scala"],
    "r programming": ["r programming", "r language"],
    "dart": ["dart"],
    "bash": ["bash", "bash scripting"],
    "powershell": ["powershell"],

    # Frontend development
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular", "angularjs"],
    "vue.js": ["vue.js", "vuejs"],
    "next.js": ["next.js", "nextjs"],
    "nuxt.js": ["nuxt.js", "nuxtjs"],
    "svelte": ["svelte"],
    "redux": ["redux"],
    "tailwind css": ["tailwind css", "tailwindcss"],
    "bootstrap": ["bootstrap"],
    "sass": ["sass"],
    "webpack": ["webpack"],
    "vite": ["vite"],
    "web accessibility": ["web accessibility", "accessibility"],

    # Backend and APIs
    "node.js": ["node.js", "nodejs"],
    "express.js": ["express.js", "expressjs"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "django": ["django"],
    "spring boot": ["spring boot", "springboot"],
    "asp.net": ["asp.net", "asp net"],
    ".net": [".net", "dotnet"],
    "laravel": ["laravel"],
    "ruby on rails": ["ruby on rails", "rails framework"],
    "rest api": ["rest api", "restful api", "restful services"],
    "graphql": ["graphql"],
    "grpc": ["grpc"],
    "microservices": ["microservices", "micro-services"],
    "websockets": ["websockets", "web sockets"],
    "oauth": ["oauth", "oauth2"],
    "jwt": ["jwt", "json web token"],

    # Databases and storage
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "sqlite": ["sqlite"],
    "mongodb": ["mongodb", "mongo db"],
    "redis": ["redis"],
    "oracle database": ["oracle database", "oracle db"],
    "microsoft sql server": ["sql server", "microsoft sql server"],
    "cassandra": ["cassandra"],
    "elasticsearch": ["elasticsearch", "elastic search"],
    "dynamodb": ["dynamodb", "dynamo db"],
    "firebase": ["firebase"],
    "supabase": ["supabase"],
    "neo4j": ["neo4j"],
    "database design": ["database design"],
    "database normalization": ["database normalization"],

    # Data analytics and engineering
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "data analysis": ["data analysis", "data analytics"],
    "data engineering": ["data engineering"],
    "etl": ["etl", "extract transform load"],
    "elt": ["elt"],
    "apache spark": ["apache spark", "pyspark"],
    "apache kafka": ["apache kafka", "kafka"],
    "apache airflow": ["apache airflow", "airflow"],
    "dbt": ["dbt"],
    "duckdb": ["duckdb"],
    "hadoop": ["hadoop", "apache hadoop"],
    "snowflake": ["snowflake"],
    "databricks": ["databricks"],
    "google bigquery": ["google bigquery", "bigquery"],
    "azure data factory": ["azure data factory"],
    "delta lake": ["delta lake"],
    "data modeling": ["data modeling", "data modelling"],
    "data warehousing": ["data warehousing", "data warehouse"],
    "excel": ["excel", "microsoft excel"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "looker": ["looker"],
    "statistics": ["statistics", "statistical analysis"],

    # AI, machine learning and GenAI
    "machine learning": ["machine learning"],
    "deep learning": ["deep learning"],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "computer vision": ["computer vision"],
    "generative ai": ["generative ai", "genai"],
    "large language models": [
        "large language models",
        "large language model",
        "llms",
        "llm",
    ],
    "rag": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag",
    ],
    "ai agents": ["ai agents", "ai agent"],
    "prompt engineering": ["prompt engineering"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "keras": ["keras"],
    "hugging face": ["hugging face", "huggingface"],
    "langchain": ["langchain"],
    "llamaindex": ["llamaindex", "llama index"],
    "openai api": ["openai api"],
    "vector databases": ["vector database", "vector databases"],
    "pinecone": ["pinecone"],
    "weaviate": ["weaviate"],
    "chroma": ["chroma db", "chromadb"],
    "faiss": ["faiss"],
    "mlflow": ["mlflow"],
    "model evaluation": ["model evaluation"],
    "feature engineering": ["feature engineering"],
    "mlops": ["mlops"],

    # Cloud platforms
    "aws": ["aws", "amazon web services"],
    "microsoft azure": ["microsoft azure", "azure"],
    "google cloud": ["google cloud platform", "gcp"],
    "cloud computing": ["cloud computing"],
    "serverless": ["serverless computing", "serverless"],
    "aws lambda": ["aws lambda"],
    "amazon s3": ["amazon s3", "aws s3"],
    "azure functions": ["azure functions"],
    "cloud security": ["cloud security"],

    # DevOps and infrastructure
    "git": ["git"],
    "github": ["github"],
    "gitlab": ["gitlab"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "jenkins": ["jenkins"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "helm": ["helm"],
    "prometheus": ["prometheus"],
    "grafana": ["grafana"],
    "ci/cd": [
        "ci/cd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
    ],
    "linux": ["linux"],
    "nginx": ["nginx"],
    "apache": ["apache http server"],
    "infrastructure as code": ["infrastructure as code"],
    "monitoring and observability": ["observability"],
    "github actions": ["github actions"],

    # Software engineering and architecture
    "data structures and algorithms": [
        "data structures and algorithms",
        "dsa",
    ],
    "object-oriented programming": [
        "object-oriented programming",
        "object oriented programming",
        "oops",
    ],
    "design patterns": ["design patterns"],
    "system design": ["system design"],
    "distributed systems": ["distributed systems"],
    "concurrency": ["concurrency"],
    "multithreading": ["multithreading", "multi-threading"],
    "agile": ["agile methodology", "agile"],
    "scrum": ["scrum"],
    "test-driven development": ["test-driven development", "tdd"],

    # Testing and quality assurance
    "unit testing": ["unit testing", "unit tests"],
    "pytest": ["pytest"],
    "junit": ["junit"],
    "selenium": ["selenium"],
    "playwright": ["playwright"],
    "cypress": ["cypress"],
    "postman": ["postman"],
    "api testing": ["api testing"],
    "integration testing": ["integration testing"],
    "load testing": ["load testing"],
    "sonarqube": ["sonarqube", "sonar qube"],

    # Cybersecurity
    "cybersecurity": ["cybersecurity", "cyber security"],
    "owasp": ["owasp"],
    "penetration testing": ["penetration testing", "pen testing"],
    "siem": ["siem"],
    "identity and access management": [
        "identity and access management",
        "iam",
    ],
    "vulnerability assessment": ["vulnerability assessment"],
    "secure coding": ["secure coding"],
}




def find_skills(text: str) -> list[str]:
    """Find recognized skills without matching partial words."""
    found = []
    normalized_text = text.lower()

    # Check longer aliases first to prioritize specific technology names.
    for skill, aliases in sorted(
        SKILL_ALIASES.items(),
        key=lambda item: max(
            (len(alias) for alias in item[1]),
            default=0,
        ),
        reverse=True,
    ):
        for alias in sorted(aliases, key=len, reverse=True):
            alias = alias.lower().strip()

            # Match the complete alias, not a part of another word.
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

            if re.search(pattern, normalized_text):
                found.append(skill)
                break

    return found



# Skill categories help explain what the resume matches.
SKILL_CATEGORIES = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c", "c++",
        "c#", "go", "rust", "php", "ruby", "kotlin", "swift",
        "scala", "r programming", "dart", "bash", "powershell",
    ],
    "Frontend": [
        "html", "css", "react", "angular", "vue.js", "next.js",
        "nuxt.js", "svelte", "redux", "tailwind css", "bootstrap",
        "sass", "webpack", "vite", "web accessibility",
    ],
    "Backend and APIs": [
        "node.js", "express.js", "fastapi", "flask", "django",
        "spring boot", "asp.net", ".net", "laravel",
        "ruby on rails", "rest api", "graphql", "grpc",
        "microservices", "websockets", "oauth", "jwt",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis",
        "oracle database", "microsoft sql server", "cassandra",
        "elasticsearch", "dynamodb", "firebase", "supabase",
        "neo4j", "database design", "database normalization",
    ],
    "Data Engineering and Analytics": [
        "pandas", "numpy", "data analysis", "data engineering",
        "etl", "elt", "apache spark", "apache kafka",
        "apache airflow", "dbt", "duckdb", "hadoop", "snowflake",
        "databricks", "google bigquery", "azure data factory",
        "delta lake", "data modeling", "data warehousing",
        "excel", "power bi", "tableau", "looker", "statistics",
    ],
    "AI and Machine Learning": [
        "machine learning", "deep learning",
        "natural language processing", "computer vision",
        "generative ai", "large language models", "rag", "ai agents",
        "prompt engineering", "tensorflow", "pytorch",
        "scikit-learn", "keras", "hugging face", "langchain",
        "llamaindex", "openai api", "vector databases", "pinecone",
        "weaviate", "chroma", "faiss", "mlflow",
        "model evaluation", "feature engineering", "mlops",
    ],
    "Cloud and DevOps": [
        "aws", "microsoft azure", "google cloud", "cloud computing",
        "serverless", "aws lambda", "amazon s3", "azure functions",
        "cloud security", "docker", "kubernetes", "jenkins",
        "terraform", "ansible", "helm", "prometheus", "grafana",
        "ci/cd", "linux", "nginx", "apache",
        "infrastructure as code", "monitoring and observability",
        "github actions",
    ],
    "Software Engineering": [
        "data structures and algorithms",
        "object-oriented programming", "design patterns",
        "system design", "distributed systems", "concurrency",
        "multithreading", "agile", "scrum",
        "test-driven development",
    ],
    "Testing and QA": [
        "unit testing", "pytest", "junit", "selenium",
        "playwright", "cypress", "postman", "api testing",
        "integration testing", "load testing", "sonarqube",
    ],
    "Cybersecurity": [
        "cybersecurity", "owasp", "penetration testing", "siem",
        "identity and access management",
        "vulnerability assessment", "secure coding",
    ],
}


# Role signals are simple rules, not a machine-learning classifier.
ROLE_RULES = {
    "Full-Stack Developer": [
        "full stack", "full-stack", "fullstack",
    ],
    "Frontend Developer": [
        "frontend developer", "front-end developer",
        "frontend engineer", "front end engineer",
        "ui developer",
    ],
    "Backend Developer": [
        "backend developer", "back-end developer",
        "backend engineer", "back end engineer",
    ],
    "Data Engineer": [
        "data engineer", "data engineering",
    ],
    "Data Analyst": [
        "data analyst", "business intelligence analyst",
        "bi analyst",
    ],
    "AI/ML Engineer": [
        "machine learning engineer", "ml engineer",
        "ai engineer", "artificial intelligence engineer",
        "genai engineer", "generative ai engineer",
    ],
    "DevOps / Cloud Engineer": [
        "devops engineer", "cloud engineer",
        "site reliability engineer", "sre engineer",
    ],
    "Cybersecurity Specialist": [
        "cybersecurity analyst", "security engineer",
        "penetration tester", "security analyst",
    ],
    "QA / Test Engineer": [
        "qa engineer", "quality assurance engineer",
        "test engineer", "automation tester",
    ],
    "Software Development Engineer": [
        "software development engineer", "software engineer",
        "software developer", "sde",
    ],
}


def detect_job_role(job_description: str) -> str:
    """Detect a role from explicit job-title phrases when possible."""
    normalized = job_description.lower()

    # Prefer a recognizable job title near the beginning.
    # This reduces the chance that a passing mention later determines
    # the role.
    opening = normalized[:500]

    for role, phrases in ROLE_RULES.items():
        for phrase in phrases:
            pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
            if re.search(pattern, opening):
                return role

    return "Other"


def get_skill_breakdown(skills: list[str]) -> dict:
    """Group recognized skills by category."""
    breakdown = {}

    for category, category_skills in SKILL_CATEGORIES.items():
        found = [
            skill for skill in skills
            if skill in category_skills
        ]

        if found:
            breakdown[category] = {
                "count": len(found),
                "skills": found,
            }

    return breakdown



def generate_recommendations(
    missing_skills: list[str],
    job_role: str,
) -> list[dict]:
    """Generate practical recommendations for missing skills."""

    learning_resources = {
        "python": "Practice Python fundamentals and solve coding problems.",
        "sql": "Practice SELECT, JOIN, GROUP BY, subqueries, and window functions.",
        "fastapi": "Build a REST API with validation, error handling, and tests.",
        "docker": "Containerize a small application and learn Dockerfiles.",
        "aws": "Learn cloud fundamentals and deploy a small application.",
        "git": "Practice branching, commits, merging, and pull requests.",
        "pytest": "Write unit tests and API tests for a Python project.",
        "react": "Build reusable components and practice React state management.",
        "javascript": "Practice functions, arrays, objects, promises, and async/await.",
        "mysql": "Practice database design, joins, indexes, and query optimization.",
        "postgresql": "Practice SQL queries, indexes, constraints, and transactions.",
        "rest api": "Learn HTTP methods, status codes, request validation, and API design.",
        "machine learning": "Learn model training, evaluation, and data preprocessing.",
        "java": "Practice Java OOP, collections, exception handling, and coding problems.",
        "spring boot": "Build a small REST service and learn dependency injection.",
    }

    recommendations = []

    for skill in missing_skills:
        action = learning_resources.get(
            skill.lower(),
            f"Study {skill} fundamentals and build a small project demonstrating it.",
        )

        recommendations.append({
            "skill": skill,
            "reason": (
                f"{skill} was recognized in the job description "
                "but not found in the resume."
            ),
            "suggestion": action,
            "project_idea": (
                f"Build a small {skill} project relevant to "
                f"a {job_role} role."
            ),
        })

    return recommendations




def get_skill_weight(skill: str, job_description: str) -> int:
    """Give preferred skills weight 1 and other skills weight 2."""
    importance = classify_skill_importance(
        skill,
        job_description,
    )

    return 1 if importance == "Preferred" else 2





def classify_skill_importance(
    skill: str,
    job_description: str,
) -> str:
    """Classify a skill using section headings and sentence-level wording."""

    required_pattern = re.compile(
        r"\b(required|must have|must-have|essential|mandatory|"
        r"minimum qualifications|basic qualifications)\b",
        re.IGNORECASE,
    )

    preferred_pattern = re.compile(
        r"\b(preferred|preferably|nice to have|nice-to-have|"
        r"bonus|desirable|optional)\b|\bplus\b",
        re.IGNORECASE,
    )

    required_heading = re.compile(
        r"\b(required qualifications|required skills|requirements|"
        r"minimum qualifications|basic qualifications|"
        r"must-have skills)\b",
        re.IGNORECASE,
    )

    preferred_heading = re.compile(
        r"\b(preferred qualifications|preferred skills|"
        r"nice to have|nice-to-have|bonus skills)\b",
        re.IGNORECASE,
    )

    other_heading = re.compile(
        r"\b(responsibilities|job summary|about the role|"
        r"what you will do|what we value|education|"
        r"qualifications|what we are looking for)\b",
        re.IGNORECASE,
    )

    aliases = SKILL_ALIASES.get(skill.lower(), [skill])
    classifications = []
    current_section = "Standard"

    for line in job_description.splitlines():
        clean_line = line.strip().lower()

        if not clean_line:
            continue



        # Update the active section using the complete line.
        if required_heading.search(clean_line):
            current_section = "Required"

        elif preferred_heading.search(clean_line):
            current_section = "Preferred"

        elif other_heading.search(clean_line) or (
            clean_line.endswith(":")
            and not find_skills(clean_line)
            and not required_pattern.search(clean_line)
            and not preferred_pattern.search(clean_line)
        ):
            # Recognize other headings and reset to Standard.
            current_section = "Standard"



        # Separate sentences so one skill's priority does not
        # accidentally affect another skill on the same line.
        sentences = re.split(r"(?<=[.!?])\s+", clean_line)

        for sentence in sentences:
            found_on_sentence = any(
                re.search(
                    r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)",
                    sentence,
                )
                for alias in aliases
            )

            if not found_on_sentence:
                continue

            if required_pattern.search(sentence):
                classifications.append("Required")
            elif preferred_pattern.search(sentence):
                classifications.append("Preferred")
            else:
                classifications.append(current_section)

    # Required takes priority if a skill appears multiple times.
    if "Required" in classifications:
        return "Required"

    if "Preferred" in classifications:
        return "Preferred"

    return "Standard"




@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "CareerMatch AI backend is running!",
    }


@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Validate the uploaded file and job description.
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide a job description.",
        )

    content = await resume.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The PDF must be 5 MB or smaller.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    # 2. Extract readable text from the PDF.
    try:
        reader = PdfReader(BytesIO(content))

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Please upload an unlocked PDF.",
            )

        resume_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please try another file.",
        ) from exc

    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found. "
                "Scanned PDFs may need OCR, which is not supported yet."
            ),
        )

    # 3. Detect skills and the job role.
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)
    job_role = detect_job_role(job_description)

    matched_skills = [
        skill for skill in job_skills
        if skill in resume_skills
    ]
    missing_skills = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    # 4. Calculate weighted skill coverage.
    skill_weights = {
        skill: get_skill_weight(skill, job_description)
        for skill in job_skills
    }

    skill_importance = {
    skill: classify_skill_importance(skill, job_description)
    for skill in job_skills
    }

    total_skill_weight = sum(skill_weights.values())
    matched_skill_weight = sum(
        skill_weights[skill]
        for skill in matched_skills
    )

    match_score = (
        round(matched_skill_weight / total_skill_weight * 100)
        if total_skill_weight > 0
        else 0
    )

    # 5. Generate recommendations for missing skills.
    recommendations = generate_recommendations(
        missing_skills,
        job_role,
    )

    # 6. Return all fields used by the frontend.
    result =  {
        "filename": resume.filename,
        "match_score": match_score,
        "matched_skill_weight": matched_skill_weight,
        "total_skill_weight": total_skill_weight,
        "required_skill_count": sum(
    1 for importance in skill_importance.values()
    if importance == "Required"
    ),
    "preferred_skill_count": sum(
    1 for importance in skill_importance.values()
    if importance == "Preferred"
    ),
    "standard_skill_count": sum(
    1 for importance in skill_importance.values()
    if importance == "Standard"
    ),
    "required_matched_count": sum(
    1 for skill in matched_skills
    if skill_importance.get(skill) == "Required"
    ),
    "preferred_matched_count": sum(
    1 for skill in matched_skills
    if skill_importance.get(skill) == "Preferred"
    ),
    "standard_matched_count": sum(
    1 for skill in matched_skills
    if skill_importance.get(skill) == "Standard"
    ),
        "score_method": "Weighted skill coverage",
        "skill_importance": skill_importance,
        "score_available": total_skill_weight > 0,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "recommendations": recommendations,
        "job_role": job_role,
        "resume_skill_breakdown": get_skill_breakdown(resume_skills),
        "job_skill_breakdown": get_skill_breakdown(job_skills),
        "matched_skill_breakdown": get_skill_breakdown(matched_skills),
        "resume_text_length": len(resume_text),
        "message": (
            "Analysis complete."
            if job_skills
            else "No recognized skills found in the job description."
        ),
    }

    history = AnalysisHistory(
        filename=resume.filename or "resume.pdf",
        job_description=job_description.strip(),
        match_score=result["match_score"],
        result=result,
    )

    try:
        db.add(history)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save the analysis to the database.",
        )

    return result


@app.get("/api/history")
def get_analysis_history(
    db: Session = Depends(get_db),
):
    records = (
        db.query(AnalysisHistory)
        .order_by(AnalysisHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "filename": record.filename,
            "job_description": record.job_description,
            "match_score": record.match_score,
            "created_at": record.created_at,
            "result": record.result,
        }
        for record in records
    ]