# Use Ubuntu as the base image
FROM ubuntu:latest

# Set environment variables to prevent prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt update && apt install -y python3 python3-pip curl \
    && pip3 install --no-cache-dir uvicorn playwright 

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Copy the rest of the application files
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
