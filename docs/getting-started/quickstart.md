# Quickstart

Dieser Quickstart zeigt den typischen Start-Flow mit cirobotix.

## 1) Projekt-Skelett initialisieren

```bash
cirobotix command=init path=. force=false
```

Erwartetes Ergebnis:

- `.codegen/`
- `tasks/`

## 2) Beispiel-Task prüfen

```bash
cat tasks/test_output_checker.yaml
```

## 3) Weiterer Workflow

Die nachfolgenden Schritte (`draft`, `ai-draft-workorder`, `promote-workorder`, `generate`) werden in der CLI-Referenz beschrieben.
