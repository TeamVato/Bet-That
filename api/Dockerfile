FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy API code
COPY api/ ./api/
COPY storage/ ./storage/

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
