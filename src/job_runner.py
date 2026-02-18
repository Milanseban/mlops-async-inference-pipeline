import json
import logging
from datetime import datetime
from pathlib import Path
import os

from src.storage import LocalArtifactStore

# ----------------------------
# Project root + runtime paths
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

STATUS_DIR = RUNTIME_DIR / "statuses"
ARTIFACTS_DIR = RUNTIME_DIR / "artifacts"

STATUS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logging.getLogger().setLevel(logging.INFO)


def write_status(run_id: str, status: str):
    path = STATUS_DIR / f"{run_id}.json"
    payload = {
        "run_id": run_id,
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def run_job():
    input_path_str = os.getenv("INPUT_PATH")
    if not input_path_str:
        raise RuntimeError("INPUT_PATH not provided to job")

    run_id = os.getenv("RUN_ID")
    if not run_id:
        raise RuntimeError("RUN_ID not provided to job")

    INPUT_PATH = Path(input_path_str)

    logging.info("Job started")

    MODE = os.getenv("MODE", "batch")
    if MODE != "inference":
        raise ValueError(f"Unsupported MODE: {MODE}")

    if not INPUT_PATH.exists():
        raise FileNotFoundError("Input file not found")

    artifact_name = os.getenv("ARTIFACT_NAME", "output.json")
    artifact_key = f"{run_id}/{artifact_name}"

    STORE_TYPE = os.getenv("STORE_TYPE", "local")

    if STORE_TYPE == "s3":
        from src.storage import S3ArtifactStore
        store = S3ArtifactStore(
            bucket_name=os.environ["S3_BUCKET"],
            prefix="artifacts"
        )
    else:
        store = LocalArtifactStore(ARTIFACTS_DIR)

    write_status(run_id, "running")

    try:
        # Idempotency check
        if store.exists(artifact_key):
            write_status(run_id, "completed")
            logging.info("Artifact already exists. Skipping execution.")
            return

        start_time = datetime.now()

        with INPUT_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        values = data.get("values", [])
        if not values:
            raise ValueError("Inference input is empty")

        model_path = PROJECT_ROOT / "models" / "model_metadata_v1.json"
        if not model_path.exists():
            raise FileNotFoundError("Model metadata not found")

        with model_path.open("r", encoding="utf-8") as f:
            model = json.load(f)

        multiplier = model["multiplier"]
        predictions = [v * multiplier for v in values]

        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        result = {
            "run_id": run_id,
            "mode": "inference",
            "model_version": model["model_version"],
            "metrics": {
                "run_duration_ms": duration_ms,
                "num_inputs": len(values),
                "num_predictions": len(predictions),
            },
            "input": values,
            "predictions": predictions,
        }

        store.write_json(artifact_key, result)
        write_status(run_id, "completed")

        logging.info(
            "Inference metrics | duration_ms=%d inputs=%d predictions=%d",
            duration_ms,
            len(values),
            len(predictions),
        )

    except Exception:
        write_status(run_id, "failed")
        raise


if __name__ == "__main__":
    run_job()
