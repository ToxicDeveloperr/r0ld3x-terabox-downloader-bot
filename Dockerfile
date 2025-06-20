# First, specify the base Docker image for Python Actors
FROM apify/actor-python:3.13

# Copy requirements.txt first for better Docker layer caching
COPY requirements.txt./

# Install Python packages and display versions for debugging
RUN echo "Python version:" \
    && python --version \
    && echo "Pip version:" \
    && pip --version \
    && echo "Installing dependencies from requirements.txt:" \
    && pip install -r requirements.txt \
    && echo "All installed Python packages:" \
    && pip freeze

# Copy the remaining source code files
COPY../

# Use compileall to ensure all Python code is valid
RUN python3 -m compileall -q.

# Launch your main.py file as the entry point
CMD python3 main.py
