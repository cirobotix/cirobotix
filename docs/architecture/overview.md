# Architektur – Überblick

## Zielbild

cirobotix setzt auf eine **deterministische Verarbeitungspipeline** statt auf frei formulierte Einzelschritte.
Der Einstieg erfolgt über die CLI in `main.py`, welche die Befehle `draft`, `ai-draft-workorder`, `promote-workorder` und `generate` an Services delegiert.

## Leitprinzipien

- **Trennung von Verantwortung**: CLI, Services, Modelle, Maschinen, Writer/Loader.
- **Expliziter Prozess**: Jeder Pipeline-Schritt ist als Machine nachvollziehbar.
- **Fail-fast Qualität**: Bei Qualitätsfehlern kann der Lauf sofort abbrechen.
- **Artefaktorientiert**: Work Orders, Reviews, Responses und Ziel-Dateien sind zentrale Ergebnisse.

## Systemgrenzen

```text
CLI -> Service Layer -> ProductionLine (Machines) -> Datei-/Code-Artefakte
```

- **Innerhalb des Systems**: Draft-Erstellung, Prompting, Ausführung, Checks, Apply, Format, Tests.
- **Außerhalb des Systems**: CI/CD-Deployment und Release-Orchestrierung.

## Kernobjekte

- **WorkOrder**: Auftragsdaten für eine konkrete Ausführung.
- **ProductionProfile**: Laufzeit- und Qualitätsverhalten.
- **ProjectContext**: Informationen über das Zielprojekt.
- **ProductionContext**: transportiert Zustand und Ergebnisse durch die Pipeline.

## Laufzeitfluss (high level)

1. CLI liest Argumente und wählt den Befehl.
2. Service lädt WorkOrder/Projekt/Profil.
3. Service baut die `ProductionLine` mit Machines auf.
4. `ProductionLine` führt Machines sequentiell aus und sammelt Step-Resultate.
5. Fehler werden im Context protokolliert; bei `fail_on_quality_error` wird abgebrochen.
