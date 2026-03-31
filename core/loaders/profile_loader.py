from pathlib import Path

import yaml

from core.models.profile import ProductionProfile


class ProfileLoader:
    def __init__(self, profiles_dir: str = "config/profiles") -> None:
        self.profiles_dir = Path(profiles_dir)

    def load(self, profile_name: str) -> ProductionProfile:
        if not profile_name or not profile_name.strip():
            raise ValueError("profile_name must be a non-empty string.")

        profile_path = self.profiles_dir / f"{profile_name}.yaml"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile file not found: {profile_path}")

        data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"Profile file must contain a YAML mapping: {profile_path}")

        return ProductionProfile(
            llm_model=data.get("llm_model", "gpt-4o-mini"),
            run_local_tests=data.get("run_local_tests", True),
            test_command=data.get("test_command", ["pytest"]),
            pythonpath_root=data.get("pythonpath_root", "."),
            use_code_formatter=data.get("use_code_formatter", False),
            formatter_command=data.get("formatter_command", []),
            fail_on_quality_error=data.get("fail_on_quality_error", True),
        )
