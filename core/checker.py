import re
from pathlib import Path

from .context import ProductionContext


class OutputChecker:
    def run(self, context: ProductionContext) -> ProductionContext:
        base = Path(".codegen") / "requests" / context.work_order.request_id
        response_path = base / "response.md"

        if not response_path.exists():
            raise FileNotFoundError("response.md not found")

        content = response_path.read_text(encoding="utf-8")
        files = self._extract_files(content)

        errors: list[str] = []

        expected_files = set(context.work_order.writable_files)
        returned_files = set(files.keys())

        missing_files = expected_files - returned_files
        unexpected_files = returned_files - expected_files

        for path in sorted(missing_files):
            errors.append(f"Missing output file block: {path}")

        for path in sorted(unexpected_files):
            errors.append(f"Unexpected output file block: {path}")

        for path in sorted(expected_files & returned_files):
            code = files[path]

            if not code.strip():
                errors.append(f"Empty output block for file: {path}")
                continue

            errors.extend(self._check_generic_file(path, code))

        if errors:
            print("\n❌ CHECK FAILED:")
            for err in errors:
                print(f"- {err}")
            raise ValueError("Output validation failed")

        print("\n✅ CHECK PASSED")
        return context

    def _extract_files(self, content: str) -> dict[str, str]:
        pattern = r"### FILE: (.+?)\n```(?:python)?\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        files: dict[str, str] = {}
        for path, code in matches:
            files[path.strip()] = code.strip()

        return files

    def _check_generic_file(self, path: str, code: str) -> list[str]:
        errors: list[str] = []

        if path.endswith(".py"):
            errors.extend(self._check_python_file(path, code))

        return errors

    def _check_python_file(self, path: str, code: str) -> list[str]:
        errors: list[str] = []

        if "```" in code:
            errors.append(f"Nested code fence found in file block: {path}")

        if not code.strip():
            errors.append(f"Python file block is empty: {path}")

        return errors
