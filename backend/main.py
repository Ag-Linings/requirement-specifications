
import os
import json
import re
import uuid
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key

# Set up Perplexity API key
perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

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
    api_key: Optional[str] = None  # Optional API key from frontend

class Requirement(BaseModel):
    id: str
    description: str
    category: str

class RequirementsResponse(BaseModel):
    requirements: List[Requirement]
    summary: Optional[str] = None

@app.post("/refine", response_model=RequirementsResponse)
async def refine_requirements(req_input: RequirementInput, request: Request) -> Dict:
    if not req_input.input.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    try:
        # Check if API key is provided in the request
        api_key = req_input.api_key or perplexity_api_key
        
        # Try Perplexity API first
        if api_key:
            try:
                return await process_requirements_with_perplexity(req_input.input, api_key)
            except Exception as e:
                print(f"Perplexity API error: {str(e)}")
                # If Perplexity fails, try web search fallback
                try:
                    return await perplexity_web_search_fallback(req_input.input)
                except Exception as web_e:
                    print(f"Web search fallback error: {str(web_e)}")
                    # If web search fails, fall back to OpenAI
                    if openai_api_key:
                        return await process_requirements_with_llm(req_input.input)
                    # Finally fall back to mock
                    return process_requirements_mock(req_input.input)
        
        # If no Perplexity API key, try OpenAI
        if openai_api_key:
            return await process_requirements_with_llm(req_input.input)
        
        # Fallback to mock processing if no API keys
        return process_requirements_mock(req_input.input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing requirements: {str(e)}")

async def process_requirements_with_perplexity(input_text: str, api_key: str) -> Dict:
    """Process requirements using Perplexity AI."""
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
    3. Provide a detailed, descriptive summary of the system described by these requirements, 
       mentioning key entities and their relationships (e.g., "A system to manage a library with Books, 
       Members, Librarians, and Borrowing records. Members can borrow books, librarians can manage 
       inventory and member accounts.")
    
    Format your response as valid JSON with this structure:
    {
      "requirements": [
        {
          "id": "REQ-1",
          "description": "The system shall...",
          "category": "functional"
        }
      ],
      "summary": "A detailed description of the system's purpose and key features."
    }
    """
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'llama-3.1-sonar-small-128k-online',  # Using the 8B parameter model
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': input_text
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 2000,
                'frequency_penalty': 1,
                'presence_penalty': 0
            },
            timeout=30  # Add timeout to prevent hanging
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")
        
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        
        # Try to parse the returned JSON
        try:
            parsed_response = json.loads(content)
            
            # Validate the response structure
            if 'requirements' not in parsed_response:
                raise ValueError("Response missing 'requirements' field")
                
            # Format the requirements
            requirements = []
            for i, req in enumerate(parsed_response.get('requirements', [])):
                requirements.append({
                    'id': req.get('id', f"REQ-{i+1}"),
                    'description': req.get('description', ''),
                    'category': req.get('category', 'unknown')
                })
                
            return {
                'requirements': requirements,
                'summary': parsed_response.get('summary', '')
            }
        except json.JSONDecodeError:
            # If the response isn't valid JSON, extract requirements using regex
            return extract_requirements_from_text(content, input_text)
            
    except Exception as e:
        print(f"Perplexity API error: {str(e)}")
        raise

async def perplexity_web_search_fallback(input_text: str) -> Dict:
    """Fallback method that searches Perplexity website for requirements extraction."""
    search_query = f"analyze and categorize software requirements: {input_text}"
    
    try:
        # We'll use a direct search query to perplexity.ai
        # In a production environment, you should use their official API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(f"https://www.perplexity.ai/search?q={search_query}", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Search returned status code {response.status_code}")
        
        # Extract text from the response
        soup = BeautifulSoup(response.text, 'html.parser')
        answer_divs = soup.find_all('div', class_=lambda c: c and 'answer' in c)
        
        answer_text = ""
        for div in answer_divs:
            answer_text += div.get_text() + "\n"
        
        if not answer_text:
            raise Exception("Could not extract answer from search results")
        
        # Extract requirements from the text
        return extract_requirements_from_text(answer_text, input_text)
        
    except Exception as e:
        print(f"Web search fallback error: {str(e)}")
        raise

def extract_requirements_from_text(text: str, original_input: str) -> Dict:
    """Extract requirements from unstructured text."""
    categories = [
        "functional", "non-functional", "constraints", 
        "interface", "business", "security", "performance"
    ]
    
    # Simple heuristic to identify requirements
    lines = text.split('\n')
    requirements = []
    req_id = 1
    
    # Extract things that look like requirements
    req_pattern = re.compile(r'.*(?:shall|should|must|will|needs to|is required to|can).*')
    
    for line in lines:
        line = line.strip()
        if len(line) > 15 and req_pattern.match(line):
            # Try to identify category
            category = "functional"  # Default category
            for cat in categories:
                if cat in line.lower():
                    category = cat
                    break
            
            requirements.append({
                "id": f"REQ-{req_id}",
                "description": line,
                "category": category
            })
            req_id += 1
    
    # If we couldn't extract requirements, create some from the original input
    if not requirements:
        sentences = re.split(r'[.!?]', original_input)
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) > 10:
                category = categories[i % len(categories)]
                requirements.append({
                    "id": f"REQ-{i+1}",
                    "description": sentence,
                    "category": category
                })
    
    # Extract or generate a summary
    summary_pattern = re.compile(r'.*(?:system|application|platform|software).*(?:is|provides|enables|allows).*')
    summary = ""
    
    for line in lines:
        if summary_pattern.match(line) and len(line) > 30:
            summary = line
            break
    
    if not summary:
        # Generate a generic summary
        entities = extract_entities(original_input)
        if entities:
            summary = f"A system for managing {', '.join(entities[:-1])}" + (f" and {entities[-1]}" if entities else "") + "."
        else:
            summary = "A software system implementing the specified requirements."
    
    return {
        "requirements": requirements,
        "summary": summary
    }

def extract_entities(text: str) -> List[str]:
    """Extract potential entities from input text."""
    # Look for capitalized words that might be entities
    entity_pattern = re.compile(r'\b[A-Z][a-z]+s?\b')
    potential_entities = entity_pattern.findall(text)
    
    # Filter common non-entities
    common_words = {"The", "A", "An", "This", "That", "These", "Those", "It", "System"}
    entities = [e for e in potential_entities if e not in common_words]
    
    return entities[:5]  # Limit to top 5 entities

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
    3. Provide a detailed, descriptive summary of the system described by these requirements, 
       mentioning key entities and their relationships (e.g., "A system to manage a library with Books, 
       Members, Librarians, and Borrowing records. Members can borrow books, librarians can manage 
       inventory and member accounts.")
    
    Format your response as valid JSON with this structure:
    {
      "requirements": [
        {
          "id": "REQ-1",
          "description": "The system shall...",
          "category": "functional"
        }
      ],
      "summary": "A detailed description of the system's purpose and key features."
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
        return json.loads(result)
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fallback to mock if OpenAI fails
        return process_requirements_mock(input_text)

def process_requirements_mock(input_text: str) -> Dict:
    """
    Mock processing function when APIs are not available.
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
    
    # Try to extract entities for a better summary
    entities = extract_entities(input_text)
    summary = "This system aims to provide a requirements management solution."
    
    if entities:
        summary = f"A system for managing {', '.join(entities[:-1])}" + (f" and {entities[-1]}" if entities else "") + "."
    
    return {
        "requirements": requirements,
        "summary": summary
    }

@app.get("/")
async def root():
    return {"message": "Requirements Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
