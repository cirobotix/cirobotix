# Architektur – Datenfluss

## End-to-End Ablauf

```text
Task/WorkOrder
  -> Loader (WorkOrder, Project, Profile)
  -> ProductionContext
  -> ProductionLine (Machines)
  -> Runtime-Artefakte + StepResults + Errors
  -> Ziel-Dateien / Tests / Ausgabe
```

## Schritt 1: Input-Laden

- WorkOrder wird geladen.
- Projektkontext wird geladen.
- Profil wird geladen.
- Blueprint wird über die Registry aufgelöst.

Ergebnis: initialer `ProductionContext`.

## Schritt 2: Kontext-Anreicherung

`ContextAssembler`, `PromptBuilder` und `ReviewBuilder` erweitern den Context,
bevor die eigentliche Ausführung startet.

## Schritt 3: Ausführung und Qualität

`Executor` erzeugt die Antwort. Danach folgen strukturierte Qualitäts- und Apply-Schritte:

- `OutputChecker` validiert die Antwortstruktur
- `OutputApplier` schreibt Ziel-Dateien
- `Formatter` normalisiert Code
- `TestRunner` prüft die Änderungen

## Schritt 4: Ergebnis und Fehlerverhalten

Die `ProductionLine` schreibt für jeden Schritt ein `StepResult` in den Context.

Bei Fehlern:
- Fehler wird in `context.errors` aufgenommen
- abhängig vom Profil wird fail-fast abgebrochen oder fortgesetzt

## Wichtige Artefakte im Lauf

- `.codegen/requests/<request_id>/task.yaml`
- `.codegen/requests/<request_id>/review.md`
- Runtime-/Response-Dateien
- angewendete Projektdateien
