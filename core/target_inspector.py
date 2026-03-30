import ast
from pathlib import Path
from typing import Optional

from .project_context import ProjectContext
from .target_analysis import ImportAnalysis, MethodAnalysis, TargetAnalysis


class TargetInspector:
    def inspect(
        self,
        *,
        project: ProjectContext,
        target_path: str,
        target_import_path: str,
        target_kind: str,
        target_name: str,
    ) -> TargetAnalysis:
        file_path = project.resolve(target_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Target file not found: {target_path}")

        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        direct_imports = self._extract_imports(tree)
        direct_project_imports = self._resolve_project_imports(
            project=project,
            imports=direct_imports,
            current_file_path=target_path,
        )

        if target_kind == "class":
            class_node = self._find_class(tree, target_name)
            method_analyses = self._extract_method_analyses(class_node)
            public_methods = [
                method.name for method in method_analyses if not method.name.startswith("_")
            ]
            referenced_symbols = self._collect_referenced_symbols_from_methods(method_analyses)

            return TargetAnalysis(
                target_path=target_path,
                target_import_path=target_import_path,
                target_kind=target_kind,
                target_name=target_name,
                class_name=target_name,
                public_methods=public_methods,
                direct_imports=direct_imports,
                direct_project_imports=direct_project_imports,
                referenced_symbols=referenced_symbols,
                method_analyses=method_analyses,
            )

        raise ValueError(f"Unsupported target_kind: {target_kind}")

    def _extract_imports(self, tree: ast.AST) -> list[ImportAnalysis]:
        imports: list[ImportAnalysis] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportAnalysis(
                            module=alias.name,
                            imported_names=[],
                            is_relative=False,
                            relative_level=0,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imported_names = [alias.name for alias in node.names]

                imports.append(
                    ImportAnalysis(
                        module=module,
                        imported_names=imported_names,
                        is_relative=(node.level > 0),
                        relative_level=node.level,
                    )
                )

        return imports

    def _resolve_project_imports(
        self,
        *,
        project: ProjectContext,
        imports: list[ImportAnalysis],
        current_file_path: str,
    ) -> list[str]:
        resolved: list[str] = []

        for item in imports:
            candidates = self._build_candidate_paths(
                project=project,
                item=item,
                current_file_path=current_file_path,
            )

            for candidate in candidates:
                if project.resolve(candidate).exists():
                    if candidate not in resolved:
                        resolved.append(candidate)
                    break

        return resolved

    def _build_candidate_paths(
        self,
        project: ProjectContext,
        item: ImportAnalysis,
        current_file_path: str,
    ) -> list[str]:
        candidates: list[str] = []

        if item.is_relative:
            candidates.extend(
                self._build_relative_candidate_paths(
                    item=item,
                    current_file_path=current_file_path,
                )
            )
            return candidates

        module_path = item.module.replace(".", "/") if item.module else ""

        if module_path:
            candidates.append(f"{module_path}.py")
            candidates.append(f"{module_path}/__init__.py")

        for imported_name in item.imported_names:
            if module_path:
                candidates.append(f"{module_path}/{imported_name}.py")

        return candidates

    def _find_class(self, tree: ast.AST, class_name: str) -> ast.ClassDef:
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        raise ValueError(f"Class not found: {class_name}")

    def _extract_method_analyses(self, class_node: ast.ClassDef) -> list[MethodAnalysis]:
        analyses: list[MethodAnalysis] = []

        for node in class_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue

            parameter_type_names = self._extract_parameter_type_names(node)
            return_type_name = self._extract_return_type_name(node)
            referenced_attribute_names = self._extract_referenced_attribute_names(node)

            analyses.append(
                MethodAnalysis(
                    name=node.name,
                    parameter_type_names=parameter_type_names,
                    return_type_name=return_type_name,
                    referenced_attribute_names=referenced_attribute_names,
                )
            )

        return analyses

    def _extract_parameter_type_names(self, node: ast.FunctionDef) -> list[str]:
        type_names: list[str] = []

        all_args = list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs)

        for arg in all_args:
            if arg.annotation is None:
                continue

            annotation_name = self._annotation_to_name(arg.annotation)
            if annotation_name and annotation_name not in type_names:
                type_names.append(annotation_name)

        return type_names

    def _extract_return_type_name(self, node: ast.FunctionDef) -> Optional[str]:
        if node.returns is None:
            return None
        return self._annotation_to_name(node.returns)

    def _annotation_to_name(self, annotation: ast.AST) -> Optional[str]:
        if isinstance(annotation, ast.Name):
            return annotation.id

        if isinstance(annotation, ast.Attribute):
            parts: list[str] = []
            current = annotation
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))

        if isinstance(annotation, ast.Subscript):
            return self._annotation_to_name(annotation.value)

        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            return annotation.value

        return None

    def _extract_referenced_attribute_names(self, node: ast.FunctionDef) -> list[str]:
        names: list[str] = []

        for child in ast.walk(node):
            if isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name):
                    value_name = child.value.id
                    full_name = f"{value_name}.{child.attr}"
                    if full_name not in names:
                        names.append(full_name)

        return names

    def _collect_referenced_symbols_from_methods(
        self,
        method_analyses: list[MethodAnalysis],
    ) -> list[str]:
        symbols: list[str] = []

        for analysis in method_analyses:
            for type_name in analysis.parameter_type_names:
                if type_name not in symbols:
                    symbols.append(type_name)

            if analysis.return_type_name and analysis.return_type_name not in symbols:
                symbols.append(analysis.return_type_name)

            for attr_name in analysis.referenced_attribute_names:
                if attr_name not in symbols:
                    symbols.append(attr_name)

        return symbols

    def _build_relative_candidate_paths(
        self,
        *,
        item: ImportAnalysis,
        current_file_path: str,
    ) -> list[str]:
        candidates: list[str] = []

        current_dir = Path(current_file_path).parent
        base_dir = current_dir

        for _ in range(max(item.relative_level - 1, 0)):
            base_dir = base_dir.parent

        if item.module:
            module_path = item.module.replace(".", "/")
            candidates.append(str(base_dir / f"{module_path}.py"))
            candidates.append(str(base_dir / module_path / "__init__.py"))

            for imported_name in item.imported_names:
                candidates.append(str(base_dir / module_path / f"{imported_name}.py"))
        else:
            for imported_name in item.imported_names:
                candidates.append(str(base_dir / f"{imported_name}.py"))

        return candidates
