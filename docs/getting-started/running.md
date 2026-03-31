# Projekt ausführen

Der aktuelle Workflow folgt drei Schritten.

## 1) AI Draft erstellen

```bash
make ai-draft TASK=tasks/test_output_checker.yaml
```

## 2) Proposal promoten

```bash
make promote REQUEST_ID=test_output_checker
```

## 3) Generierung ausführen

```bash
make generate REQUEST_ID=test_output_checker
```

## Ergebnis

Nach erfolgreichem Lauf findest du die erzeugten Artefakte unter `.codegen/requests/<request_id>/`.
