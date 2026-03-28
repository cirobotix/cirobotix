from typing import Protocol

from .context import ProductionContext


class Machine(Protocol):
    def run(self, context: ProductionContext) -> ProductionContext: ...
