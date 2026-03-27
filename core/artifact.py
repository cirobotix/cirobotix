from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class ArtifactType:
    name: str
    required_fields: List[str]
    description: str = ""


@dataclass
class ArtifactRequest:
    artifact_type: str
    payload: Dict[str, Any]
    request_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
