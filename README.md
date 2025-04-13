
# Requirements Manager

A microservice for the virtual Software Engineering Lab that refines natural language requirements into structured specification lists.

## Overview

This application accepts user input in natural language describing software requirements and uses an LLM to convert the raw input into a clean, categorized specification list.

## Features

- Natural language input for system requirements
- LLM-powered transformation to structured requirements
- Categorization (Functional, Non-functional, Constraints, etc.)
- Clean, responsive user interface
- Kubernetes deployment ready

## Tech Stack

- **Frontend:** React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI
- **LLM:** OpenAI API (with fallback mock processing)
- **Infrastructure:** Docker, Kubernetes

## Local Development

### Frontend

```bash
# Install dependencies
npm install

# Run the frontend in development mode
npm run dev
```

### Backend

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

## Docker

Build and run the application using Docker:

```bash
# Build the Docker image
docker build -t requirements-manager .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here requirements-manager
```

## Kubernetes Deployment

1. Create the OpenAI API key secret (replace with your actual API key):

```bash
# Create the secret file from template
export API_KEY=your_openai_api_key
export BASE64_ENCODED_API_KEY=$(echo -n $API_KEY | base64)
sed "s/\${BASE64_ENCODED_API_KEY}/$BASE64_ENCODED_API_KEY/g" kubernetes/secret.yaml.template > kubernetes/secret.yaml

# Apply the secret
kubectl apply -f kubernetes/secret.yaml
```

2. Deploy the application:

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

The application will be accessible at `/requirements` path via your Kubernetes Ingress.

## Endpoints

- `GET /` - Health check endpoint
- `POST /refine` - Refine natural language requirements

## License

MIT
