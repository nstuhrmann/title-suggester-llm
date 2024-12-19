# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY scripts/ ./scripts/
COPY config/ ./config/

# Set environment variables (override in docker-compose or .env)
ENV PYTHONUNBUFFERED=1

# Run the script

CMD ["python", "scripts/main.py"]

