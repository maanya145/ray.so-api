# Use Ubuntu as the base image
FROM ubuntu:latest

# Set environment variables to prevent prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt update && apt install -y python3 python3-pip python3-venv curl \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create and activate a virtual environment
RUN python3 -m venv /app/venv

# Use the virtual environment for all installations
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements first (leveraging Docker caching)
COPY requirements.txt .

# Install Python dependencies inside the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

#Install Playwright dependencies
RUN playwright install-deps

# Copy the rest of the application files
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
