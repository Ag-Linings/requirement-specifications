
import os
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
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
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "****")
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

# Initialize the database and tables if they don't exist
def init_db():
    try:
        # Create a connection without specifying database
        temp_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = temp_conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        cursor.execute(f"USE {MYSQL_DB}")
        
        # Create requirements table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id VARCHAR(36) PRIMARY KEY,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            user_id VARCHAR(100)
        )
        """)
        
        temp_conn.commit()
        cursor.close()
        temp_conn.close()
        print("Database initialized successfully")
    except Error as e:
        print(f"Error initializing database: {e}")
        raise HTTPException(status_code=500, detail="Database initialization error")

# Call init_db at startup
@app.on_event("startup")
async def startup_event():
    init_db()

# ------------------ Pydantic Schemas ------------------ #

class RequirementInput(BaseModel):
    input: str
    user_id: Optional[str] = None

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
        # Process the requirements either via mock or OpenAI
        if not openai_api_key:
            result = process_requirements_mock(req_input.input)
        else:
            result = await process_requirements_with_llm(req_input.input)

        # Logging the result before saving to the database
        print(f"Received requirements to save: {result['requirements']}")

        # Save to MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        for req in result["requirements"]:
            # Generate a unique ID for the requirement
            req_id = str(uuid.uuid4())

            # Insert the requirement into the database
            cursor.execute(
                "INSERT INTO requirements (id, description, category, user_id) VALUES (%s, %s, %s, %s)",
                (req_id, req["description"], req["category"], req_input.user_id)
            )
            
            # Update the ID in the result to match what's stored in the database
            req["id"] = req_id
            
            print(f"Adding requirement: {req}")

        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()

        print("Database commit successful.")
        return result
    except Exception as e:
        print(f"Error processing requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing requirements: {str(e)}")

# ------------------ Database Operations ------------------ #

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

# ------------------ Fallback (Mock) ------------------ #

@dataclass
class MockRequirement:
    id: str
    description: str
    category: str

def categorize_sentence(sentence: str) -> str:
    sentence_lower = sentence.lower()
    if any(k in sentence_lower for k in ["must", "should", "shall", "allow", "support"]):
        return "functional"
    elif any(k in sentence_lower for k in ["response time", "throughput", "latency"]):
        return "performance"
    elif any(k in sentence_lower for k in ["encrypt", "authentication", "authorization", "secure"]):
        return "security"
    elif any(k in sentence_lower for k in ["interface", "api", "ui", "ux"]):
        return "interface"
    elif any(k in sentence_lower for k in ["legal", "budget", "timeframe", "deadline"]):
        return "constraints"
    elif any(k in sentence_lower for k in ["business", "stakeholder", "goal", "objective"]):
        return "business"
    elif any(k in sentence_lower for k in ["uptime", "availability", "reliability"]):
        return "non-functional"
    else:
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

@app.get("/")
async def root():
    return {"message": "Requirements Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
