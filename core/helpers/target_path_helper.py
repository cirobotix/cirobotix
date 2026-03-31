from pathlib import Path


class TargetPathHelper:
    def to_import_path(self, target_path: str) -> str:
        path = Path(target_path)
        without_suffix = path.with_suffix("")
        return ".".join(without_suffix.parts)

    def to_test_path(self, target_path: str) -> str:
        path = Path(target_path)
        return str(Path("tests") / path.parent / f"test_{path.name}")
