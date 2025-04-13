
# Build stage for React frontend
FROM node:20-alpine as frontend-build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Backend stage with Python
FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY backend/ ./backend/
COPY --from=frontend-build /app/dist /app/dist

# Install backend dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose the port
EXPOSE 8000

# Start the application
CMD ["python", "backend/main.py"]
