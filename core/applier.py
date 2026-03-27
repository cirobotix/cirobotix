from pathlib import Path
import re


class OutputApplier:
    def apply(self, request_id: str) -> list[Path]:
        base = Path(".codegen") / "requests" / request_id
        response_path = base / "response.md"

        if not response_path.exists():
            raise FileNotFoundError("response.md not found")

        content = response_path.read_text(encoding="utf-8")
        files = self._extract_files(content)

        written_files: list[Path] = []

        for relative_path, code in files.items():
            target = Path(relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code.rstrip() + "\n", encoding="utf-8")
            written_files.append(target)

        return written_files

    def _extract_files(self, content: str) -> dict[str, str]:
        pattern = r"### FILE: (.+?)\n```python\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        files: dict[str, str] = {}
        for path, code in matches:
            files[path.strip()] = code.strip()

        if not files:
            raise ValueError("No file blocks found in response")

        return files
