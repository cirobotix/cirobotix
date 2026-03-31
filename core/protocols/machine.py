from typing import Protocol

from core.models.context import ProductionContext


class Machine(Protocol):
    def run(self, context: ProductionContext) -> ProductionContext: ...
