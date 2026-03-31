# Architektur – Komponenten

## 1) CLI-Schicht

Die CLI ist der Prozess-Einstieg und verteilt Befehle auf Services.

Verantwortung:
- Argumente lesen
- Kommandos auflösen
- Ergebnisse für den Nutzer ausgeben

## 2) Service-Schicht

Die Service-Schicht koordiniert Business-Abläufe und baut die Pipeline zusammen.

Wichtige Services:
- `WorkOrderCliService` (Draft/Generate)
- `WorkOrderProposalService` (AI-Proposal + Promotion)

## 3) Registry & Blueprints

Blueprints werden in einer Registry registriert und anhand des Namens aufgelöst.
Dadurch kann die Pipeline mit unterschiedlichen Blueprint-Typen arbeiten, ohne die Laufzeitlogik zu ändern.

## 4) Loader / Writer

- **Loader** laden Konfiguration, Profile, Tasks und Projektinformationen.
- **Writer** schreiben WorkOrder-, Review- und Runtime-Artefakte.

Diese Trennung macht I/O explizit und testbar.

## 5) Pipeline-Machines

Die `ProductionLine` verarbeitet eine Liste von Machines in fester Reihenfolge.

Beispiele in der Standardreihenfolge:

1. `Validator`
2. `ContextAssembler`
3. `PromptBuilder`
4. `ReviewBuilder`
5. `WorkOrderCliRuntimeWriter`
6. `Executor`
7. `OutputChecker`
8. `OutputApplier`
9. `Formatter`
10. `TestRunner`

## 6) Domain-Modelle

Kernmodelle (`core/models`) bilden den Zustand und die Verträge der Pipeline:
- `WorkOrder`
- `ProductionContext`
- `ProductionProfile`
- `StepResult`

Sie bilden den stabilen Austausch zwischen Services und Machines.
