# Base image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment named rvenv
RUN python -m venv /app/rvenv

# Ensure venv Python and pip are used
ENV PATH="/app/rvenv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python deps into rvenv
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY backend/ backend/
COPY frontend/ frontend/
COPY start.sh /start.sh

# Ensure startup script is executable
RUN chmod +x /start.sh

# Expose ports (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000
EXPOSE 8501

# Default command
CMD ["/start.sh"]
