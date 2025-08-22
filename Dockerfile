# Use Python 3.11 Alpine as base image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./backend ./backend
COPY ./frontend ./frontend

# Expose ports
EXPOSE 8000 8501

# Create a startup script
RUN echo '#!/bin/sh' > start.sh && \
    echo 'cd /app/frontend && streamlit run main.py --server.port=8501 --server.address=0.0.0.0 &' >> start.sh && \
    echo 'cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000' >> start.sh && \
    chmod +x start.sh

# Run both services
CMD ["./start.sh"]