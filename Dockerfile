# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the working directory
COPY huntbot.py .

# Set the command to run your script
CMD ["python", "huntbot.py"]

# Create a Docker volume
VOLUME /app/data