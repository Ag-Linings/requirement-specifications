import os
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import mysql.connector
from dataclasses import dataclass
from mysql.connector import Error

# Set up OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key

# MySQL database configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DB = os.getenv("MYSQL_DB", "requirements_db")

# ------------------ FASTAPI SETUP ------------------ #

app = FastAPI(title="Requirements Manager")

# CORS config for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ MySQL Connection Setup ------------------ #

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

def init_db():
    try:
        server_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        server_cursor.close()
        server_conn.close()

        db_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        db_cursor = db_conn.cursor()
        db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id VARCHAR(100) PRIMARY KEY,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            user_id VARCHAR(100)
        )
        """)
        db_conn.commit()
        db_cursor.close()
        db_conn.close()
        print("Database and table initialized successfully")
    except Error as e:
        print(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail="Database initialization error")

@app.on_event("startup")
async def startup_event():
    init_db()

# ------------------ Pydantic Schemas ------------------ #

class RequirementInput(BaseModel):
    input: str
    user_id: str  # Now mandatory

class Requirement(BaseModel):
    id: str
    description: str
    category: str

class RequirementsResponse(BaseModel):
    requirements: List[Requirement]
    summary: Optional[str] = None

# ------------------ Main Endpoint ------------------ #

@app.post("/refine", response_model=RequirementsResponse)
async def refine_requirements(req_input: RequirementInput) -> Dict:
    if not req_input.input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")

    try:
        if not openai_api_key:
            result = process_requirements_mock(req_input.input)
        else:
            result = await process_requirements_with_llm(req_input.input)

        print(f"Received requirements to save: {result['requirements']}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Count existing requirements for the user
        cursor.execute("SELECT COUNT(*) FROM requirements WHERE user_id = %s", (req_input.user_id,))
        current_count = cursor.fetchone()[0]

        for i, req in enumerate(result["requirements"], start=1):
            req_id = f"{req_input.user_id}_{current_count + i}"

            cursor.execute(
                "INSERT INTO requirements (id, description, category, user_id) VALUES (%s, %s, %s, %s)",
                (req_id, req["description"], req["category"], req_input.user_id)
            )
            req["id"] = req_id
            print(f"Adding requirement: {req}")

        conn.commit()
        cursor.close()
        conn.close()

        print("Database commit successful.")
        return result
    except Exception as e:
        print(f"Error processing requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing requirements: {str(e)}")

# ------------------ Get Requirements ------------------ #

@app.get("/requirements", response_model=RequirementsResponse)
async def get_requirements(user_id: Optional[str] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if user_id:
            cursor.execute(
                "SELECT id, description, category FROM requirements WHERE user_id = %s",
                (user_id,)
            )
        else:
            cursor.execute("SELECT id, description, category FROM requirements")

        requirements = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"requirements": requirements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving requirements: {str(e)}")

# ------------------ OpenAI LLM Function ------------------ #

async def process_requirements_with_llm(input_text: str) -> Dict:
    system_prompt = """
    You are a requirements engineering expert. Your task is to analyze raw requirements and:
    1. Extract distinct requirements from the text
    2. Categorize each requirement into one of the following types:
       - functional, non-functional, constraints, interface, business, security, performance
    3. Provide a brief summary of the system

    Format as JSON:
    {
      "requirements": [
        {"id": "REQ-1", "description": "The system shall...", "category": "functional"}
      ],
      "summary": "A brief summary."
    }
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    import json
    return json.loads(result)

# ------------------ Fallback Mock ------------------ #

@dataclass
class MockRequirement:
    id: str
    description: str
    category: str

def categorize_sentence(sentence: str) -> str:
    sentence_lower = sentence.lower()
    
    # Functional Requirement: Checks for verbs and system actions
    if any(k in sentence_lower for k in ["must", "should", "shall", "allow", "support", "perform", "manage"]):
        return "functional"
    
    # Performance: Checks for performance-related terms
    elif any(k in sentence_lower for k in ["response time", "throughput", "latency", "speed", "scalability"]):
        return "performance"
    
    # Security: Checks for security-related terms
    elif any(k in sentence_lower for k in ["encrypt", "authentication", "authorization", "secure", "privacy"]):
        return "security"
    
    # Interface: Checks for UI, UX, and API-related terms
    elif any(k in sentence_lower for k in ["interface", "api", "ui", "ux", "user interface", "integration"]):
        return "interface"
    
    # Constraints: Checks for time, legal, or budget constraints
    elif any(k in sentence_lower for k in ["legal", "budget", "timeframe", "deadline", "limit", "constraint"]):
        return "constraints"
    
    # Business: Business goals and stakeholder-related terms
    elif any(k in sentence_lower for k in ["business", "stakeholder", "goal", "objective", "profit", "target"]):
        return "business"
    
    # Non-functional: Availability, reliability, and general system qualities
    elif any(k in sentence_lower for k in ["uptime", "availability", "reliability", "quality", "maintenance"]):
        return "non-functional"
    
    # Default to functional if no specific category is found
    return "functional"
def process_requirements_mock(input_text: str) -> Dict:
    sentences = [s.strip() for s in input_text.split('.') if len(s.strip()) > 10]
    requirements: List[MockRequirement] = []

    for i, sentence in enumerate(sentences):
        req_id = f"REQ-{i+1}"
        category = categorize_sentence(sentence)
        requirements.append(MockRequirement(id=req_id, description=sentence, category=category))

    return {
        "requirements": [r.__dict__ for r in requirements],
        "summary": "Mock summary of extracted requirements."
    }

# ------------------ Root Endpoint ------------------ #

@app.get("/")
async def root():
    return {"message": "Requirements Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
