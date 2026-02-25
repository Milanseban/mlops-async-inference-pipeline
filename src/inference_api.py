from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
import subprocess
import uuid
import os
import sys

app = FastAPI()


# Project root + runtime paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

REQUESTS_DIR = RUNTIME_DIR / "requests"
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/infer")
def run_inference(payload: dict):
    # ----- validate request schema -----
    if "values" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'values' key")

    run_id = str(uuid.uuid4())

    # ----- write per-request input file -----
    input_path = REQUESTS_DIR / f"{run_id}.json"
    with input_path.open("w", encoding="utf-8") as f:
        json.dump({"values": payload["values"]}, f)

    # ----- prepare environment for job -----
    env = os.environ.copy()
    env["MODE"] = "inference"
    env["INPUT_PATH"] = str(input_path)
    env["RUN_ID"] = run_id

    # ----- trigger job asynchronously -----
    subprocess.Popen(
        [sys.executable, "-m", "src.job_runner"],
        cwd=PROJECT_ROOT,
        env=env,
    )

    return {
        "status": "accepted",
        "run_id": run_id
    }


@app.get("/status/{run_id}")
def get_status(run_id: str):
    status_path = RUNTIME_DIR / "statuses" / f"{run_id}.json"

    if not status_path.exists():
        raise HTTPException(status_code=404, detail="Run ID not found")

    with status_path.open("r", encoding="utf-8") as f:
        status = json.load(f)

    return status
