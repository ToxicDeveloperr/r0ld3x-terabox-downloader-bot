# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# ---- MODIFICATION START ----
# Install build-essential which contains gcc and other necessary tools
# This needs to be done BEFORE pip install
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
# ---- MODIFICATION END ----

# Copy requirements
COPY requirements.txt .

# Install dependencies
# Now pip will find gcc and be able to build tgcrypto
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
