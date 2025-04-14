
import os
from typing import Dict, List, Optional, Union
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Set up OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key

app = FastAPI(title="Requirements Manager")

# Configure CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequirementInput(BaseModel):
    input: str

class Requirement(BaseModel):
    id: str
    description: str
    category: str

class RequirementsResponse(BaseModel):
    requirements: List[Requirement]
    summary: Optional[str] = None

@app.post("/refine", response_model=RequirementsResponse)
async def refine_requirements(req_input: RequirementInput) -> Dict:
    if not req_input.input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    try:
        # Check if OpenAI API key is set
        if not openai_api_key:
            # Fallback to mock processing if no API key
            return process_requirements_mock(req_input.input)
        
        return await process_requirements_with_llm(req_input.input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing requirements: {str(e)}")

async def process_requirements_with_llm(input_text: str) -> Dict:
    """Process requirements using OpenAI."""
    system_prompt = """
    You are a requirements engineering expert. Your task is to analyze raw requirements and:
    1. Extract distinct requirements from the text
    2. Categorize each requirement into one of the following types:
       - functional (features and capabilities)
       - non-functional (quality attributes)
       - constraints (limitations and restrictions)
       - interface (UI/UX and external systems interaction)
       - business (organizational goals and needs)
       - security (data and system protection)
       - performance (speed, efficiency, scalability)
    
    Format your response as valid JSON with this structure:
    {
      "requirements": [
        {
          "id": "REQ-1",
          "description": "The system shall...",
          "category": "functional"
        }
      ]
    }
    
    DO NOT include a summary field in your response.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Use appropriate model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Extract JSON from response
        result = response.choices[0].message.content
        return result
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to mock if OpenAI fails
        return process_requirements_mock(input_text)

def process_requirements_mock(input_text: str) -> Dict:
    """
    Mock processing function when OpenAI API is not available.
    Extracts lines and assigns categories based on content.
    """
    import random
    
    # Split the input text by newlines to get individual requirements
    requirements_lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    requirements = []
    categories = {
        "UI Performance": "interface",
        "initial page": "performance",
        "user input": "performance",
        "render": "performance",
        "display": "interface",
        "database": "performance",
        "data": "performance",
        "search": "functional",
        "API": "interface",
        "cache": "performance",
        "encrypt": "security",
        "compress": "non-functional",
        "validate": "functional",
        "authenticate": "security",
        "brute-force": "security",
        "log": "non-functional",
        "factor authentication": "security",
        "concurrent": "performance",
        "scale": "performance",
        "store": "non-functional",
        "instances": "constraints",
        "peak load": "performance"
    }
    
    for i, line in enumerate(requirements_lines):
        req_id = f"REQ-{i+1}"
        
        # Try to determine category based on keywords
        category = "performance"  # Default category
        for keyword, cat in categories.items():
            if keyword.lower() in line.lower():
                category = cat
                break
        
        requirements.append(
            Requirement(
                id=req_id,
                description=line,
                category=category
            )
        )
    
    return {
        "requirements": requirements
    }

@app.get("/")
async def root():
    return {"message": "Requirements Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
