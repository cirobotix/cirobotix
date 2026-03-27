from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class ArtifactRequest:
    blueprint_name: str
    payload: Dict[str, Any]
    request_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
