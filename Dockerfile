# Use a slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (needed by PyMuPDF)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Run the server using shell form so $PORT is expanded
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}