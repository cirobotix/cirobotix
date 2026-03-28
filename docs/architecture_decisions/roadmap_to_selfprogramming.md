# 🏭 Development Roadmap – Codegen Manufacturing System

## 🎯 Ziel

Dieses Dokument beschreibt die nächsten Entwicklungsschritte zur Weiterentwicklung des Codegen-Systems hin zu einer stabilen, erweiterbaren und industriell gedachten Plattform.

Der Fokus liegt darauf:

* die bestehende Architektur zu stabilisieren
* Erweiterbarkeit sicherzustellen
* das System zur Selbstweiterentwicklung vorzubereiten

---

# 🧩 Aktueller Stand (Erreicht)

Das System verfügt bereits über:

* Blueprint (Bauplan)
* WorkOrder (Fertigungsauftrag)
* ProductionProfile (Kalibrierung)
* ProductionContext (Werkstückzustand)
* Machine (Ausführungseinheit)
* ProductionLine (Orchestrierung)
* StepResult / Trace (Produktionsprotokoll)
* Formatter (deterministische Nachbearbeitung)

👉 Das Architecture Target Model ist erfolgreich implementiert.

---

# 🧭 Nächste Entwicklungsphasen

---

# 🏗️ Phase 1: Architektur stabilisieren

## 1. Blueprints aus `main.py` auslagern

### Problem

Blueprint ist aktuell hart im Einstieg definiert.

### Ziel

* Trennung von Orchestrierung und Produktdefinition
* Wiederverwendbarkeit

### Umsetzung

* `core/blueprints/` einführen
* z. B.:

  * `python_registry_class.py`
  * `blueprint_catalog.py`

---

## 2. WorkOrders entkoppeln

### Problem

WorkOrder ist aktuell fest im Code definiert.

### Ziel

* System kann beliebige Aufträge verarbeiten

### Umsetzung

* WorkOrder aus JSON/YAML oder Factory laden
* `main.py` wird generisch

---

## 3. Maschinen logisch gruppieren

### Zielstruktur

* Preparation Machines
* Generation Machines
* Quality Machines
* Application Machines
* Delivery Machines

### Hinweis

Noch kein Code-Umbau nötig – zunächst konzeptionelle Ordnung.

---

# 🧠 Phase 2: System erweiterbar machen

## 4. Mehrere Blueprints unterstützen

### Ziel

System soll nicht nur Registry bauen, sondern mehrere Artefakttypen:

Beispiele:

* Service-Klasse
* Dataclass
* Testmodul
* Config-Klasse

### Nutzen

Testet echte Generalisierbarkeit der Architektur

---

## 5. OutputChecker blueprint-gesteuert machen

### Problem

Checker ist aktuell hart auf Registry-Usecase ausgelegt

### Ziel

* Checks basieren auf Blueprint
* keine hardcodierten Annahmen

### Beispiel

Statt:

* fixe Klassennamen

Zukünftig:

* aus Blueprint ableiten

---

## 6. Review-Package einführen

### Ziel

Strukturierte Übergabe an Prüfung (Merge Request)

### Inhalt

* WorkOrder
* Blueprint
* StepResults
* generierte Dateien
* Testergebnisse

👉 Industriell: Übergabe an Qualitätsprüfung

---

# ⚙️ Phase 3: Kalibrierung ausbauen

## 7. Profile als Modi definieren

### Beispiele

* `fast_profile`
* `strict_profile`
* `dev_profile`

### Unterschiede

* Tests an/aus
* Formatter aktiv
* Modellwahl
* Fail-fast Verhalten

---

## 8. Formatter in zwei Maschinen aufteilen

### Statt:

* eine unscharfe Formatter-Station

### Besser:

1. `LintFixMachine`
2. `FormatMachine`

👉 bessere Nachvollziehbarkeit und Kontrolle

---

# 📊 Phase 4: Produktionsprotokoll erweitern

## 9. StepResult erweitern

### Ergänzen um:

* bearbeitete Dateien
* Dauer
* Exit-Code
* verwendeter Befehl

---

## 10. Laufzeiten messen

### Ziel

* Performance verstehen
* Bottlenecks erkennen
* Stabilität analysieren

---

# 🤖 Phase 5: Selbstanwendung (entscheidend!)

## 11. System erzeugt eigene Erweiterungen

### Ziel

Das System soll helfen, neue Komponenten zu erzeugen:

* neue Machines
* neue Blueprints
* neue Tests

👉 nicht blind automatisiert
👉 sondern kontrolliert und nachvollziehbar

---

# 🧱 Systemgrenzen (wichtig!)

## Lokales System

✔ generiert Code
✔ prüft lokal
✔ bereitet Review vor

## CI/CD Pipeline

✔ validiert
✔ integriert
✔ prüft vollständig
✔ gibt frei

👉 keine zweite CI/CD bauen!

---

# 🚀 Priorisierung

## 🔥 Priorität 1

Blueprints + WorkOrders aus `main.py` herauslösen

## 🔥 Priorität 2

OutputChecker generalisieren (Blueprint-basiert)

## 🔥 Priorität 3

ProductionProfile sinnvoll nutzen (Modi)

## 🔥 Priorität 4

Review-Package einführen

---

# 🧠 Leitprinzipien

## ❌ Nicht tun

* keine Logik in Prompts verstecken
* keine zweite Pipeline bauen
* keine impliziten Abhängigkeiten

## ✅ Tun

* klare Verantwortlichkeiten
* deterministische Schritte
* explizite Verträge
* nachvollziehbare Prozesse

---

# 🏁 Nächster konkreter Schritt

👉 **Blueprint-Katalog + WorkOrder-Quelle einführen**

Das ist der Übergang von:

* Demo-System

zu:

* echter Produktionsplattform

---

# 🧭 Abschluss

Das System ist jetzt:

👉 funktional
👉 architektonisch sauber
👉 bereit für echte Erweiterung

Ab jetzt geht es nicht mehr um „Code bauen“,
sondern um:

👉 **eine Software-Fabrik stabil weiterentwickeln**

---
