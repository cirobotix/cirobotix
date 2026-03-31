from dataclasses import dataclass, field


@dataclass(frozen=True)
class ContextDependency:
    path: str
    reason: str
    priority: str  # "required" | "helpful"


@dataclass(frozen=True)
class ContextDependencyResolution:
    required_read_files: list[str] = field(default_factory=list)
    helpful_read_files: list[str] = field(default_factory=list)
    dependencies: list[ContextDependency] = field(default_factory=list)
