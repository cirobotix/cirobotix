from .blueprint import Blueprint


class Registry:
    def __init__(self) -> None:
        self.blueprints: dict[str, Blueprint] = {}

    def register(self, blueprint: Blueprint) -> None:
        if blueprint.name in self.blueprints:
            raise ValueError(f"Blueprint already registered: {blueprint.name}")
        self.blueprints[blueprint.name] = blueprint

    def get(self, name: str) -> Blueprint:
        try:
            return self.blueprints[name]
        except KeyError as exc:
            raise ValueError(f"Unknown blueprint: {name}") from exc
