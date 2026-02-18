from abc import ABC, abstractmethod
from typing import Dict


class ArtifactStore(ABC):
    @abstractmethod
    def write_json(self, key: str, data: Dict) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
