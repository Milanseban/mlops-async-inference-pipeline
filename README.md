MLOps Async Inference Pipeline
Overview

This project implements a lightweight asynchronous ML inference pipeline with:

FastAPI-based inference API

Subprocess-based background job execution

Per-run artifact tracking

Idempotent job execution

Pluggable artifact storage (Local filesystem or AWS S3)

Docker support for reproducible deployment

The system is designed to simulate how ML inference jobs are triggered, executed, tracked, and stored in production-like environments.

Architecture Summary

Flow:

Client sends inference request to /infer

API:

Validates payload

Generates unique run_id

Writes request input to runtime/requests

Triggers job_runner asynchronously

job_runner:

Updates status (running)

Loads model metadata

Executes inference logic

Writes artifact to storage

Updates status (completed or failed)

Client polls /status/{run_id} to track job progress

Artifacts are stored either:

Locally in runtime/artifacts/

Or in AWS S3 (via boto3)

Project Structure
mlops-async-inference-pipeline/
│
├── src/
│   ├── inference_api.py        # FastAPI server
│   ├── job_runner.py           # Background job executor
│   └── storage/
│       ├── base.py             # ArtifactStore abstraction
│       ├── local.py            # Local filesystem storage
│       └── s3.py               # S3 storage implementation
│
├── models/
│   └── model_metadata_v1.json  # Example model metadata
│
├── examples/
│   ├── sample_batch_input.json
│   └── sample_inference_request.json
│
├── runtime/                    # Generated at runtime (ignored in git)
│   ├── artifacts/
│   ├── requests/
│   └── statuses/
│
├── Dockerfile
├── requirements.txt
└── .gitignore

Key Design Decisions
1. Asynchronous Execution

Inference jobs are executed via subprocess, allowing the API to return immediately while background processing continues.

2. Idempotency

Before executing a job, the system checks whether an artifact already exists for a given run_id.
If it exists, execution is skipped and status is marked completed.

3. Storage Abstraction

The ArtifactStore base class allows switching between:

Local filesystem

AWS S3

This simulates production-ready storage flexibility.

4. Runtime Separation

All generated state (requests, statuses, artifacts) lives under runtime/, keeping source code clean and version-controlled.

Running Locally
1. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows

2. Install dependencies
pip install -r requirements.txt

3. Start API
uvicorn src.inference_api:app --reload


Visit:

http://127.0.0.1:8000/docs

Example Inference Request
{
  "values": [1, 2, 3]
}

Running with Docker
Build image
docker build -t mlops-async-inference-pipeline .

Run container
docker run -p 8000:8000 mlops-async-inference-pipeline


API will be available at:

http://localhost:8000/docs

Using S3 Storage

Run Docker with environment variables:

docker run -p 8000:8000 \
  -e STORE_TYPE=s3 \
  -e S3_BUCKET=your-bucket-name \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  mlops-async-inference-pipeline


Artifacts will be written to the specified S3 bucket under the artifacts/ prefix.

What This Project Demonstrates

API-triggered ML job execution

Environment-driven configuration

Artifact versioning per run

Idempotent processing

Storage abstraction patterns

Containerized deployment readiness
