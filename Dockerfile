# Use Python 3.8 as base image
FROM python:3.8-slim

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy and install Python dependencies
COPY ./app/requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app/ /app/

# Run the Python script
CMD ["python", "main.py"]
