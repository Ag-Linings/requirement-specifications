# Build stage for React frontend
#FROM node:20-alpine as frontend-build

#WORKDIR /app
#COPY package*.json ./
#RUN npm install
#COPY . .
#RUN npm run build

# Backend stage with Python
#FROM python:3.11-slim

#WORKDIR /app

# Install shell, curl, and ping
#RUN apt-get update && \
 #   apt-get install -y --no-install-recommends \
  #  curl iputils-ping && \
   # rm -rf /var/lib/apt/lists/*

# Copy backend code
#COPY backend/ ./backend/
#COPY --from=frontend-build /app/dist /app/dist

# Install backend dependencies
#RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose the port
#EXPOSE 8000

# Start the application
#CMD ["python", "backend/main.py"]

# Use a script to wait for MySQL before starting the app
#COPY wait-for-mysql.sh /wait-for-mysql.sh
#RUN chmod +x /wait-for-mysql.sh

#CMD ["/wait-for-mysql.sh", "mysql", "3306", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl iputils-ping netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uvicorn

# Copy application code and wait script
COPY . .

COPY wait-for-mysql.sh /wait-for-mysql.sh
RUN chmod +x /wait-for-mysql.sh

# Ensure wait-for-mysql.sh exists, is executable, and has correct line endings
RUN sed -i 's/\r$//' /wait-for-mysql.sh

# Add a healthcheck for the app
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose app port
EXPOSE 8000

# Use wait script to ensure MySQL is up before starting the app
CMD ["/wait-for-mysql.sh", "mysql", "3306", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
