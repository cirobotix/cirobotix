from dataclasses import dataclass, field


@dataclass(frozen=True)
class Blueprint:
    name: str
    required_fields: list[str]
    description: str = ""
    output_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    quality_requirements: list[str] = field(default_factory=list)
