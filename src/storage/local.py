import json
from pathlib import Path
from typing import Dict

from .base import ArtifactStore


class LocalArtifactStore(ArtifactStore):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_json(self, key: str, data: Dict) -> None:
        path = self.base_path / key
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def exists(self, key: str) -> bool:
        return (self.base_path / key).exists()
