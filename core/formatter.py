import subprocess

from .context import ProductionContext


class Formatter:
    def run(self, context: ProductionContext) -> ProductionContext:
        if not context.profile.use_code_formatter:
            print("Skipping formatter because use_code_formatter is disabled.")
            return context

        if not context.profile.formatter_command:
            raise ValueError("Formatter is enabled, but no formatter_command is configured.")

        if not context.written_files:
            raise ValueError(
                "No written files available in context. Formatter must run after OutputApplier."
            )

        command = context.profile.formatter_command + [str(path) for path in context.written_files]

        print(f"Running formatter: {' '.join(command)}")

        result = subprocess.run(
            command,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Formatter failed with exit code {result.returncode}")

        return context
