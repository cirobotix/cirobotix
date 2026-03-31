from core.models.context import ProductionContext
from core.models.result import StepResult
from core.protocols.machine import Machine


class ProductionLine:
    def __init__(self, machines: list[Machine]) -> None:
        self.machines = machines

    def run(self, context: ProductionContext) -> ProductionContext:
        for machine in self.machines:
            name = machine.__class__.__name__

            try:
                context = machine.run(context)

                context.add_step_result(
                    StepResult(
                        machine_name=name,
                        success=True,
                        message="OK",
                    )
                )

            except Exception as exc:
                error_message = str(exc)

                context.add_step_result(
                    StepResult(
                        machine_name=name,
                        success=False,
                        message=error_message,
                    )
                )

                context.add_error(f"{name}: {error_message}")

                # Fail-fast Verhalten
                if context.profile.fail_on_quality_error:
                    raise

        return context
