from .artifact import ArtifactType


class Registry:
    def __init__(self) -> None:
        self.types: dict[str, ArtifactType] = {}

    def register(self, artifact: ArtifactType) -> None:
        if artifact.name in self.types:
            raise ValueError(f"Artifact type already registered: {artifact.name}")
        self.types[artifact.name] = artifact

    def get(self, name: str) -> ArtifactType:
        try:
            return self.types[name]
        except KeyError as exc:
            raise ValueError(f"Unknown artifact type: {name}") from exc
