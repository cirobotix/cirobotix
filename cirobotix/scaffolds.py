from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

SCAFFOLD_ROOT = files("cirobotix") / "scaffolds" / "base"


@dataclass
class InitResult:
    created: list[Path]
    overwritten: list[Path]
    skipped: list[Path]


class ProjectScaffolder:
    def apply(
        self,
        *,
        target_dir: Path,
        force: bool = False,
        dry_run: bool = False,
    ) -> InitResult:
        created: list[Path] = []
        overwritten: list[Path] = []
        skipped: list[Path] = []

        mapping = {
            SCAFFOLD_ROOT / "codegen": target_dir / ".codegen",
            SCAFFOLD_ROOT / "tasks": target_dir / "tasks",
        }

        for src_root, dst_root in mapping.items():
            for src in src_root.rglob("*"):
                if src.is_dir():
                    continue

                relative_path = src.relative_to(src_root)
                destination = dst_root / relative_path

                if destination.exists() and not force:
                    skipped.append(destination)
                    continue

                if destination.exists() and force:
                    overwritten.append(destination)
                else:
                    created.append(destination)

                if dry_run:
                    continue

                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        if not dry_run:
            (target_dir / ".codegen").mkdir(parents=True, exist_ok=True)
            (target_dir / "tasks").mkdir(parents=True, exist_ok=True)

        return InitResult(created=created, overwritten=overwritten, skipped=skipped)
