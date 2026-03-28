from pathlib import Path

import yaml

from .project_context import ProjectContext


class ProjectLoader:
    def load(self, path: str) -> ProjectContext:
        project_path = Path(path)

        if not project_path.exists():
            raise FileNotFoundError(f"Project config not found: {project_path}")

        data = yaml.safe_load(project_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError("Project config must contain a YAML mapping.")

        root_path = Path(data.get("root_path", ".")).resolve()

        return ProjectContext(
            root_path=root_path,
            pythonpath_root=data.get("pythonpath_root", "."),
            source_roots=data.get("source_roots", []),
            test_roots=data.get("test_roots", []),
            protected_files=data.get("protected_files", []),
        )
