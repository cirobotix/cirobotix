import sys
from typing import Optional


class CliArgsParser:
    def parse(self, argv: Optional[list[str]] = None) -> dict[str, str]:
        raw_args = argv if argv is not None else sys.argv[1:]

        parsed: dict[str, str] = {}
        for raw in raw_args:
            if "=" not in raw:
                raise ValueError(f"Argument must be key=value: {raw}")

            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(f"Argument key must not be empty: {raw}")

            if not value:
                raise ValueError(f"Argument value must not be empty: {raw}")

            parsed[key] = value

        return parsed
