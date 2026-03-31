from datetime import datetime
from pathlib import Path


class RequestIdBuilder:
    def build(self, blueprint_name: str, target_path: str) -> str:
        stem = Path(target_path).stem.replace(" ", "_").replace("-", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{blueprint_name}_{stem}_{timestamp}"
