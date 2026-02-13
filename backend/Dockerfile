# Use a slim Python 3.11 image for better performance
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
# THE FIX: Changed build_essential to build-essential
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Copy the start script, make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the FastAPI port
EXPOSE 8000

# Use the script to run seed data then start uvicorn
CMD ["/app/start.sh"]