# Python 3.8 sama dengan versi klien di Windows 7
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080

# Run the application with Waitress
CMD ["python", "serve.py"]