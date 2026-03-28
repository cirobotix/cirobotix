from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    root_path: Path
    pythonpath_root: str = "."
    source_roots: list[str] = field(default_factory=list)
    test_roots: list[str] = field(default_factory=list)
    protected_files: list[str] = field(default_factory=list)

    def resolve(self, relative_path: str) -> Path:
        return self.root_path / relative_path
