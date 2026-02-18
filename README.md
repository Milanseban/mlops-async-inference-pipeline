# MLOps Async Inference Pipeline

A lightweight asynchronous ML inference system that simulates production-style job execution, artifact tracking, and pluggable storage backends.

---

## Overview

This project implements an end-to-end ML inference workflow featuring:

- FastAPI-based inference API  
- Asynchronous background job execution via subprocess  
- Per-run artifact generation and tracking  
- Idempotent job execution  
- Pluggable storage backend (Local filesystem or AWS S3)  
- Dockerized deployment support  

The focus of this project is system design and operational ML patterns rather than model complexity.

---

## Architecture

### Inference Flow

1. Client sends a request to `/infer`  
2. API:
   - Validates input  
   - Generates a unique `run_id`  
   - Writes request payload to `runtime/requests`  
   - Triggers `job_runner` asynchronously  
3. `job_runner`:
   - Updates status to `running`  
   - Loads model metadata  
   - Executes inference logic  
   - Writes artifact to storage  
   - Updates status to `completed` or `failed`  
4. Client polls `/status/{run_id}` to track job progress  

---

## Project Structure

```
mlops-async-inference-pipeline/
│
├── src/
│   ├── inference_api.py
│   ├── job_runner.py
│   └── storage/
│       ├── base.py
│       ├── local.py
│       └── s3.py
│
├── models/
│   └── model_metadata_v1.json
│
├── examples/
│   ├── sample_batch_input.json
│   └── sample_inference_request.json
│
├── runtime/                 # Generated at runtime (gitignored)
│   ├── artifacts/
│   ├── requests/
│   └── statuses/
│
├── Dockerfile
├── requirements.txt
└── .gitignore
```

---

## Key Design Concepts

### Asynchronous Execution

Inference jobs are executed in a separate subprocess.  
The API returns immediately after triggering execution, allowing background processing.

### Idempotency

Before executing a job, the system checks whether an artifact already exists for the given `run_id`.  
If it exists, execution is skipped and the job is marked as completed.

### Storage Abstraction

The `ArtifactStore` base class enables switching between:

- Local filesystem storage  
- AWS S3 storage  

This allows environment-dependent configuration without modifying core business logic.

### Runtime Separation

All generated files (requests, statuses, artifacts) are stored under `runtime/` and excluded from version control.

---

## Running Locally

### 1. Create virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start API server

```bash
uvicorn src.inference_api:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## Example Inference Request

```json
{
  "values": [1, 2, 3]
}
```

---

## Docker Usage

### Build image

```bash
docker build -t mlops-async-inference-pipeline .
```

### Run container

```bash
docker run -p 8000:8000 mlops-async-inference-pipeline
```

Access:

```
http://localhost:8000/docs
```

---

## Running with S3 Backend

```bash
docker run -p 8000:8000 \
  -e STORE_TYPE=s3 \
  -e S3_BUCKET=your-bucket-name \
  -e AWS_ACCESS_KEY_ID=your-access-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  mlops-async-inference-pipeline
```

Artifacts will be written to the specified S3 bucket under the `artifacts/` prefix.



