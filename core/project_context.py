from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectContext:
    root_path: Path
    pythonpath_root: str = "."
    source_roots: list[str] = field(default_factory=lambda: ["core"])
    test_roots: list[str] = field(default_factory=lambda: ["tests"])
    read_files: list[str] = field(default_factory=list)
    writable_files: list[str] = field(default_factory=list)
    protected_files: list[str] = field(default_factory=list)

    def resolve(self, relative_path: str) -> Path:
        return self.root_path / relative_path

    def is_writable(self, relative_path: str) -> bool:
        return relative_path in self.writable_files

    def is_readable(self, relative_path: str) -> bool:
        return (
            relative_path in self.read_files
            or relative_path in self.writable_files
        )
