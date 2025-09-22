# src/aiassistantservice/Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# instala deps
# ou requirements.in + pip-compile antes
COPY requirements.txt .    
RUN pip install -r requirements.txt

# código
COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
