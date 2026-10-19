# Stage 1: Build the React application
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend/react-app

COPY frontend/react-app/package*.json ./
RUN npm ci

COPY frontend/react-app ./
RUN npm run build

# Stage 2: Python FastAPI backend server
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Copy built React frontend assets from stage 1
COPY --from=frontend-builder /app/frontend/react-app/dist /app/frontend/react-app/dist

# Render provides the port in the $PORT environment variable
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
