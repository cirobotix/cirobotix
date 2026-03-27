from .context import ProductionContext
from .machine import Machine


class ProductionLine:
    def __init__(self, machines: list[Machine]) -> None:
        self.machines = machines

    def run(self, context: ProductionContext) -> ProductionContext:
        for machine in self.machines:
            context = machine.run(context)
        return context
