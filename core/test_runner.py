import os
import subprocess  # nosec B404

from .context import ProductionContext


class TestRunner:
    def run(self, context: ProductionContext) -> ProductionContext:
        if not context.profile.run_local_tests:
            print("Skipping local tests because run_local_tests is disabled.")
            return context

        env = os.environ.copy()

        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            context.profile.pythonpath_root
            if not existing_pythonpath
            else f"{context.profile.pythonpath_root}{os.pathsep}{existing_pythonpath}"
        )

        print(
            f"Running tests with PYTHONPATH={context.profile.pythonpath_root}: "
            f"{' '.join(context.profile.test_command)}"
        )

        result = subprocess.run(  # nosec B603
            context.profile.test_command,
            env=env,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Pytest failed with exit code {result.returncode}")

        return context
