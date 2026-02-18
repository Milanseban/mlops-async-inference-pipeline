FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Ensure runtime folders exist
RUN mkdir -p runtime/artifacts runtime/statuses runtime/requests

# Expose FastAPI port
EXPOSE 8000

# Default environment (can be overridden)
ENV STORE_TYPE=local

# Start FastAPI app
CMD ["uvicorn", "src.inference_api:app", "--host", "0.0.0.0", "--port", "8000"]

