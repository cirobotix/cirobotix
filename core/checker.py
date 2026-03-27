from pathlib import Path
import re


class OutputChecker:
    def check(self, request_id: str) -> None:
        base = Path(".codegen") / request_id
        response_path = base / "response.md"

        if not response_path.exists():
            raise FileNotFoundError("response.md not found")

        content = response_path.read_text(encoding="utf-8")
        files = self._extract_files(content)

        errors = []

        source_path = "tool/core/generated_registry.py"
        test_path = "tests/core/test_generated_registry.py"

        if source_path not in files:
            errors.append(f"Missing source file block: {source_path}")

        if test_path not in files:
            errors.append(f"Missing test file block: {test_path}")

        if not errors:
            source_code = files[source_path]
            test_code = files[test_path]

            errors.extend(self._check_source_file(source_code))
            errors.extend(self._check_test_file(test_code))

        if errors:
            print("\n❌ CHECK FAILED:")
            for err in errors:
                print(f"- {err}")
            raise ValueError("Output validation failed")

        print("\n✅ CHECK PASSED")

    def _extract_files(self, content: str) -> dict[str, str]:
        pattern = r"### FILE: (.+?)\n```python\n(.*?)```"
        matches = re.findall(pattern, content, re.DOTALL)

        files: dict[str, str] = {}
        for path, code in matches:
            files[path.strip()] = code.strip()

        return files

    def _check_source_file(self, source_code: str) -> list[str]:
        errors: list[str] = []

        class_matches = re.findall(r"class\s+(\w+)\s*:", source_code)
        if len(class_matches) != 1:
            errors.append(f"Expected exactly one class in source file, found {len(class_matches)}")
        elif class_matches[0] != "ArtifactRegistry":
            errors.append(f"Expected class name 'ArtifactRegistry', found '{class_matches[0]}'")

        required_methods = ["register", "get", "list_names"]
        for method in required_methods:
            if f"def {method}" not in source_code:
                errors.append(f"Missing method in source file: {method}")

        if '"""' not in source_code:
            errors.append("Missing docstring in source file")

        return errors

    def _check_test_file(self, test_code: str) -> list[str]:
        errors: list[str] = []

        if "import pytest" not in test_code:
            errors.append("Missing pytest import in test file")

        if "ArtifactRegistry" not in test_code:
            errors.append("Test file does not reference ArtifactRegistry")

        test_functions = re.findall(r"def\s+(test_\w+)\s*\(", test_code)
        if len(test_functions) < 3:
            errors.append(f"Expected at least 3 test functions, found {len(test_functions)}")

        return errors
