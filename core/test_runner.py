import os
import subprocess


class TestRunner:
    def run(self) -> None:
        env = os.environ.copy()

        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = "." if not existing_pythonpath else f".{os.pathsep}{existing_pythonpath}"

        result = subprocess.run(
            ["pytest"],
            env=env,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Pytest failed with exit code {result.returncode}")
