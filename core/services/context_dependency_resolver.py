from typing import Optional

from core.models.context_dependency import ContextDependency, ContextDependencyResolution
from core.models.project_context import ProjectContext
from core.models.target_analysis import TargetAnalysis


class ContextDependencyResolver:
    def resolve(
        self,
        *,
        project: ProjectContext,
        analysis: TargetAnalysis,
    ) -> ContextDependencyResolution:
        dependencies: list[ContextDependency] = []
        seen_paths: set[str] = set()

        self._add_dependency(
            dependencies=dependencies,
            seen_paths=seen_paths,
            path=analysis.target_path,
            reason="Target module under test or modification must always be included.",
            priority="required",
        )

        for path in analysis.direct_project_imports:
            self._add_dependency(
                dependencies=dependencies,
                seen_paths=seen_paths,
                path=path,
                reason="Direct project import used by the target module.",
                priority="required",
            )

        for symbol in analysis.referenced_symbols:
            inferred_path = self._infer_path_from_symbol(symbol, project)
            if inferred_path is None:
                continue

            self._add_dependency(
                dependencies=dependencies,
                seen_paths=seen_paths,
                path=inferred_path,
                reason=f"Inferred from referenced symbol: {symbol}",
                priority="helpful",
            )

        required_read_files = [item.path for item in dependencies if item.priority == "required"]
        helpful_read_files = [item.path for item in dependencies if item.priority == "helpful"]

        return ContextDependencyResolution(
            required_read_files=required_read_files,
            helpful_read_files=helpful_read_files,
            dependencies=dependencies,
        )

    def _add_dependency(
        self,
        *,
        dependencies: list[ContextDependency],
        seen_paths: set[str],
        path: str,
        reason: str,
        priority: str,
    ) -> None:
        normalized_path = path.strip()

        if not normalized_path or normalized_path in seen_paths:
            return

        seen_paths.add(normalized_path)
        dependencies.append(
            ContextDependency(
                path=normalized_path,
                reason=reason,
                priority=priority,
            )
        )

    def _infer_path_from_symbol(
        self,
        symbol: str,
        project: ProjectContext,
    ) -> Optional[str]:
        symbol = symbol.strip()
        if not symbol:
            return None

        exact_candidate_map = {
            "context.work_order": "core/models/work_order.py",
            "context.project": "core/models/project_context.py",
            "context.profile": "core/models/profile.py",
            "context.blueprint": "core/models/blueprint.py",
        }

        for prefix, candidate in exact_candidate_map.items():
            if symbol == prefix or symbol.startswith(prefix + "."):
                if project.resolve(candidate).exists():
                    return candidate
                return None

        left_part = symbol.split(".", 1)[0]

        root_candidate_map = {
            "context": "core/models/context.py",
            "project": "core/models/project_context.py",
            "work_order": "core/models/work_order.py",
            "profile": "core/models/profile.py",
            "blueprint": "core/models/blueprint.py",
        }

        candidate = root_candidate_map.get(left_part)
        if candidate is None:
            return None

        if not project.resolve(candidate).exists():
            return None

        return candidate
