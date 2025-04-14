
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
    3. Provide a brief summary of the system described by these requirements
    
    Format your response as valid JSON with this structure:
    {
      "requirements": [
        {
          "id": "REQ-1",
          "description": "The system shall...",
          "category": "functional"
        }
      ],
      "summary": "A brief summary of the system's purpose and key features."
    }
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
    Extracts sentences and assigns random categories.
    """
    import random
    
    # Simple sentence splitting
    sentences = [s.strip() for s in input_text.split('.') if len(s.strip()) > 10]
    
    categories = [
        "functional", "non-functional", "constraints", 
        "interface", "business", "security", "performance"
    ]
    
    requirements = []
    
    for i, sentence in enumerate(sentences):
        req_id = f"REQ-{i+1}"
        category = random.choice(categories)
        requirements.append(
            Requirement(
                id=req_id,
                description=sentence,
                category=category
            )
        )
    
    return {
        "requirements": requirements,
        "summary": "This system aims to provide a requirements management solution."
    }

@app.get("/")
async def root():
    return {"message": "Requirements Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
