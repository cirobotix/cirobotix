# 🏭 Architecture Glossary – Codegen Manufacturing System

## 🎯 Ziel
Dieses Dokument definiert die zentrale Architektur und Begriffswelt unseres Code-Generierungssystems.

Das System orientiert sich bewusst an industriellen Fertigungsprozessen (MES), um:
- Determinismus zu gewährleisten
- klare Verantwortlichkeiten zu schaffen
- Skalierbarkeit und Erweiterbarkeit sicherzustellen

Wichtig:
👉 Dieses System ersetzt **keine CI/CD-Pipeline**  
👉 Die CI/CD-Pipeline ist die eigentliche Fertigungsstraße

---

# 🧩 1. Kernprinzip

Das System trennt klar zwischen:

- **Produktdefinition (Blueprint)**
- **Fertigungsauftrag (Work Order)**
- **Arbeitsgängen (Operations)**
- **Maschinen (Execution Units)**
- **Kalibrierung (Configuration)**
- **Qualitätssicherung (QA)**
- **Fertigungsstraße (CI/CD)**
- **Übergabe (Merge Request)**

---

# 📐 2. Blueprint

## Definition
Der Blueprint ist der **Bauplan eines Artefakts**.

## Verantwortung
Beschreibt:
- Struktur des Artefakts
- erwartete Dateien
- fachliche Anforderungen
- technische Constraints
- Qualitätsanforderungen

## Wichtig
- Kein Prompt!
- Kein Code!
- Kein Prozess!

👉 Der Blueprint ist die **Single Source of Truth** für das Soll.

---

# 📦 3. Work Order

## Definition
Ein konkreter **Fertigungsauftrag**, der einen Blueprint instanziiert.

## Inhalt
- request_id
- blueprint_name
- payload (konkrete Werte)
- optionale Parameter

## Beziehung
- Blueprint = Was wird gebaut
- Work Order = Dieses konkrete Teil wird gebaut

---

# ⚙️ 4. Work Order Operations

## Definition
Die einzelnen **Arbeitsgänge**, die zur Fertigung notwendig sind.

## Beispiele
- ValidateOrder
- BuildPromptMaterial
- GenerateCandidate
- CheckOutputStructure
- ApplyFiles
- NormalizeCode
- RunLocalTests
- PrepareReviewPackage

## Wichtig
👉 Operations sind **logische Arbeitsschritte**, keine Implementierung

---

# 🏗️ 5. Machine

## Definition
Eine Machine ist eine **Ausführungseinheit**, die eine Operation durchführt.

## Beispiele
- PromptBuilderMachine
- LLMExecutionMachine
- OutputCheckerMachine
- CodeFormatterMachine
- TestRunnerMachine

## Wichtig
- Eine Operation kann von verschiedenen Maschinen ausgeführt werden
- Maschinen sind austauschbar
- Maschinen sind technisch, nicht fachlich

---

# 🎛️ 6. Calibration (Production Profile)

## Definition
Die **Konfiguration und Einstellung der Maschinen**

## Beispiele
- verwendetes LLM-Modell
- Prompt-Regeln
- Formatierungsregeln (Black, Ruff)
- Teststrategie
- Fehlerverhalten
- Retry-Strategien

## Wichtig
👉 Die Pipeline bleibt gleich – die Kalibrierung verändert das Verhalten

---

# 🧪 7. Quality Assurance (QA)

## Definition
Eine Menge von **Prüfstationen entlang des Prozesses**

## Beispiele
- Output-Strukturprüfung
- Import-Prüfung
- Codeformatierung
- lokale Tests (pytest)
- spätere Pipeline-Checks

## Wichtig
👉 QA ist kein einzelner Schritt  
👉 QA ist eine **Schicht über mehrere Stationen**

---

# 🧰 8. Lokales System (Pre-Production)

## Aufgabe
Das lokale Tool übernimmt:

- Erstellung von Work Orders
- Ableitung von Prompt & Review
- Generierung von Code
- Strukturprüfung
- Anwendung von Dateien
- lokale Normalisierung (Linter/Formatter)
- lokale Tests
- Vorbereitung der Review-Daten

## Wichtig
👉 Das lokale System ist **keine CI/CD-Pipeline**

---

# 🚀 9. CI/CD Pipeline (Fertigungsstraße)

## Definition
Die CI/CD-Pipeline ist die **echte Produktionsstraße**

## Verantwortung
- vollständige QA-Gates
- reproduzierbare Umgebung
- Integrationstests
- Policy Checks
- Build-Prozess
- Freigabe

## Wichtig
👉 Diese wird NICHT lokal nachgebaut

---

# 📬 10. Merge Request

## Definition
Die formale **Übergabe des gefertigten Teils an die Prüfung**

## Bedeutung
- Teil wurde erzeugt
- lokale Checks wurden durchgeführt
- Review-Dokumentation liegt vor

## Industrielles Äquivalent
👉 Übergabe an Qualitätsprüfung / Abnahme

---

# 🧱 11. Artifact (Werkstück)

## Definition
Das aktuell erzeugte oder bearbeitete Ergebnis

## Beispiele
- generierter Code
- Testdateien
- Review-Dokumente

## Wichtig
👉 Das Artifact durchläuft alle Operations

---

# 🔄 12. Production Context

## Definition
Der Zustand des Werkstücks während der Fertigung

## Inhalt
- Work Order
- Blueprint
- erzeugte Dateien
- Zwischenstände
- Prüfergebnisse
- Logs

## Wichtig
👉 Der Context ist das **zentrale Transportmedium zwischen Maschinen**

---

# 🧭 13. Architekturgrenzen

## Lokal (dieses System)
✔ Code generieren  
✔ lokal prüfen  
✔ vorbereiten  
✔ dokumentieren  

## CI/CD Pipeline
✔ validieren  
✔ integrieren  
✔ freigeben  
✔ deployen  

---

# ⚠️ 14. Wichtige Leitregeln

## ❌ Nicht tun
- keine zweite CI/CD bauen
- keine Logik in Prompts verstecken
- keine impliziten Abhängigkeiten

## ✅ Tun
- klare Trennung von Verantwortung
- deterministische Verarbeitung
- explizite Verträge
- reproduzierbare Ergebnisse

---

# 🧠 15. Zusammenfassung

| Konzept            | Bedeutung                         |
|-------------------|----------------------------------|
| Blueprint         | Bauplan                          |
| Work Order        | Auftrag                          |
| Operation         | Arbeitsschritt                   |
| Machine           | ausführende Einheit              |
| Calibration       | Einstellung                      |
| QA                | Prüfstationen                    |
| Artifact          | Werkstück                        |
| Context           | Zustand des Werkstücks           |
| CI/CD Pipeline    | Fertigungsstraße                 |
| Merge Request     | Übergabe zur Prüfung             |

---

# 🚀 Nächster Schritt

Auf Basis dieses Glossars wird nun:
1. das Domain-Modell (Dataclasses) definiert
2. die Produktionslinie (Operations + Machines) strukturiert
3. der bestehende Code schrittweise darauf ausgerichtet