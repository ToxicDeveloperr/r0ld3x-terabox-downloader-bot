# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code files
COPY . .

# Env variables for web hosting
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV PORT=8080

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Run entrypoint
CMD ["./entrypoint.sh"]
