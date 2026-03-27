from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductionProfile:
    llm_model: str = "gpt-4o-mini"
    run_local_tests: bool = True
    test_command: list[str] = field(default_factory=lambda: ["pytest"])
    pythonpath_root: str = "."
    use_code_formatter: bool = False
    formatter_command: list[str] = field(default_factory=list)
    fail_on_quality_error: bool = True
