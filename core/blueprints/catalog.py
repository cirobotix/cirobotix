from core.registry import Registry

from .python_data_model import build_python_data_model_blueprint
from .python_registry_class import build_python_registry_class_blueprint


def register_blueprints(registry: Registry) -> None:
    registry.register(build_python_registry_class_blueprint())
    registry.register(build_python_data_model_blueprint())
