# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Change directory to /app/model, where your Flask app is located
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

ENV HOST=0.0.0.0
ENV PORT=8080
# Run the Flask app from the model directory
CMD ["python", "model.py"]


