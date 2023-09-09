# Use a slim version of Python 3.10.10 as the base image
FROM python:3.10.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy directories into the working directory
COPY ./.well-known /app/.well-known
COPY ./src /app/src

# Copy individual files the working directory
COPY logo.png main.py openapi.yaml requirements.txt /app/

# Install the Python dependencies specified in requirements.txt
RUN pip install -r /app/requirements.txt 

# Specify the default command to run the application
#CMD ["uvicorn", "main:app", "--port=8080", "--host=0.0.0.0"]
