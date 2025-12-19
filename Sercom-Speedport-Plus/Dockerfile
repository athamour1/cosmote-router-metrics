# Use Selenium standalone image with Chrome pre-installed
FROM selenium/standalone-chrome:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python and pip in the selenium/standalone-chrome image
USER root
RUN apt-get update && apt-get install -y python3 python3-pip curl

# Copy the Python script and requirements
COPY requirements.txt /app/requirements.txt
COPY speedport_script.py /app/speedport_script.py

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt --break-system-packages

# Set working directory
WORKDIR /app

# Expose port for Prometheus metrics
EXPOSE 8000

# Run the Selenium Python script
CMD ["python3", "speedport_script.py"]
