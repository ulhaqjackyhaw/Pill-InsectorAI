# Use the official Python 3.8 slim image as the base image
FROM python:3.8-slim

# Set environment variables (disables warning about development server by Flask)
ENV FLASK_ENV=production

# Set the working directory within the container
WORKDIR /app

# Install necessary system dependencies for OpenCV
# We need mesa-dev for camera stuff
RUN apt-get update && apt-get install -y \
  libglib2.0-0 \
  libsm6 \
  libxrender1 \
  libxext6 \
  libgl1-mesa-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy the application files into the container
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

# Copy the templates and static files
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY models/ /app/models/

# Install Python dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Expose port 5003 for the Flask application
# Usually we use 5000 but port 5000 is used by heaps of other things
EXPOSE 5003

# Define the command to run the Flask application using Gunicorn
# We have to use gunicorn to get https to work as well as to get the camera to work (camera access needs https)
# Can also add threads if you want to use more than one thread
# Long time out for slow CPUs
# CMD ["gunicorn", "-b", "0.0.0.0:5003", "--threads", "4", "--timeout", "120", "app:app"]
CMD ["gunicorn", "-b", "0.0.0.0:5003", "--timeout", "120", "app:app"]