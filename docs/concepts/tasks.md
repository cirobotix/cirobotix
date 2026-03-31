# Was ist ein Task?

Ein Task ist eine YAML-Datei mit einer konkreten Arbeitsanweisung für cirobotix.

## Beispiel

```yaml
task_id: test_output_checker
blueprint_name: python_pytest_unit_test
title: Create unit tests for OutputChecker
```

## Typische Bestandteile

- `task_id`: Eindeutige Kennung
- `blueprint_name`: Welcher Blueprint angewendet wird
- `title` / `description`: Fachliche Beschreibung
- `inputs`: Zielartefakte und Parameter
- `acceptance_criteria`: Konkrete Erfolgskriterien

## Quelle im Repository

Ein Beispiel liegt unter `tasks/test_output_checker.yaml`.
