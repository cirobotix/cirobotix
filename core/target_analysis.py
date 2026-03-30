from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class MethodAnalysis:
    name: str
    parameter_type_names: list[str] = field(default_factory=list)
    return_type_name: Optional[str] = None
    referenced_attribute_names: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ImportAnalysis:
    module: str
    imported_names: list[str] = field(default_factory=list)
    is_relative: bool = False
    relative_level: int = 0


@dataclass(frozen=True)
class TargetAnalysis:
    target_path: str
    target_import_path: str
    target_kind: str
    target_name: str
    class_name: Optional[str] = None
    public_methods: list[str] = field(default_factory=list)
    direct_imports: list[ImportAnalysis] = field(default_factory=list)
    direct_project_imports: list[str] = field(default_factory=list)
    referenced_symbols: list[str] = field(default_factory=list)
    method_analyses: list[MethodAnalysis] = field(default_factory=list)
