# 🏭 Architecture Target Model – Domain Objects & Production Line

## Ziel
Dieses Dokument konkretisiert das Architektur-Glossar in ein erstes technisches Zielmodell.
Der Fokus liegt auf den zentralen Domänenobjekten und ihrer Beziehung zueinander.

Wichtig:
- Das lokale Tool ist **nicht** die CI/CD-Pipeline
- Die CI/CD-Pipeline bleibt die eigentliche Fertigungsstraße
- Das lokale Tool modelliert Baupläne, Fertigungsaufträge, Arbeitsgänge und Vorprüfungen

---

# 1. Architekturprinzip

Wir schneiden das System in drei Ebenen:

## 1. Domain
Die fachlichen Kernobjekte:
- Blueprint
- WorkOrder
- Operation
- MachineCalibration / ProductionProfile
- Artifact
- ProductionContext
- StepResult / QualityResult

## 2. Execution
Die technischen Ausführer:
- Machines
- lokale Normalizer / Checker / Runner

## 3. Orchestration
Die Reihenfolge und Steuerung:
- ProductionLine
- lokale Ausführung einer WorkOrder
- Übergabe an Review / Merge Request

---

# 2. Kernobjekte

## 2.1 Blueprint
Der Blueprint beschreibt den Bauplan eines Artefakts.

### Verantwortung
- Typ des Artefakts
- Pflichtfelder
- erwartete Outputs
- Regeln und Constraints
- Qualitätsanforderungen

### Beispiel
`python_registry_class`

### Vorschlag als Dataclass
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Blueprint:
    name: str
    description: str
    required_fields: list[str]
    output_files: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    quality_requirements: list[str] = field(default_factory=list)
```

### Bedeutung
Der Blueprint ist die produktseitige Sollbeschreibung.
Er ist **nicht** der Prompt.

---

## 2.2 WorkOrder
Die WorkOrder ist der konkrete Fertigungsauftrag.

### Verantwortung
- referenziert einen Blueprint
- trägt die konkreten Werte
- identifiziert einen einzelnen Lauf

### Vorschlag als Dataclass
```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class WorkOrder:
    request_id: str
    blueprint_name: str
    payload: dict[str, Any]
```

### Bedeutung
Der Blueprint sagt: *was grundsätzlich gebaut werden soll*.
Die WorkOrder sagt: *baue dieses konkrete Teil jetzt*.

---

## 2.3 Operation
Eine Operation ist ein logischer Arbeitsschritt in der Fertigung.

### Beispiele
- ValidateOrder
- BuildPrompt
- BuildReview
- WriteRequestPackage
- GenerateOutput
- CheckOutputStructure
- ApplyOutputFiles
- NormalizeCode
- RunLocalTests
- PrepareReviewPackage

### Vorschlag als Enum
```python
from enum import Enum

class OperationName(str, Enum):
    VALIDATE_ORDER = "validate_order"
    BUILD_PROMPT = "build_prompt"
    BUILD_REVIEW = "build_review"
    WRITE_REQUEST_PACKAGE = "write_request_package"
    GENERATE_OUTPUT = "generate_output"
    CHECK_OUTPUT_STRUCTURE = "check_output_structure"
    APPLY_OUTPUT_FILES = "apply_output_files"
    NORMALIZE_CODE = "normalize_code"
    RUN_LOCAL_TESTS = "run_local_tests"
    PREPARE_REVIEW_PACKAGE = "prepare_review_package"
```

### Bedeutung
Operations sind fachlich-logische Arbeitsgänge.
Sie sind noch keine Implementierung.

---

## 2.4 MachineCalibration / ProductionProfile
Die Kalibrierung beschreibt, wie Maschinen arbeiten sollen.

### Verantwortung
- Modellwahl
- Striktheit
- lokale Prüfkommandos
- Fehlerstrategie
- Normalisierungsschritte

### Vorschlag als Dataclass
```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ProductionProfile:
    llm_model: str = "gpt-4o-mini"
    enforce_output_blocks: bool = True
    run_local_tests: bool = True
    test_command: list[str] = field(default_factory=lambda: ["pytest"])
    pythonpath_root: str = "."
    use_code_formatter: bool = False
    formatter_command: list[str] = field(default_factory=list)
    fail_on_quality_error: bool = True
```

### Bedeutung
Die Linie bleibt gleich.
Das Produktionsprofil bestimmt das Verhalten der Linie.

---

## 2.5 Artifact
Das Artifact ist das Werkstück, also das erzeugte Ergebnis oder Teil-Ergebnis.

### Beispiele
- prompt.md
- review.md
- response.md
- generierte Python-Dateien
- Testdateien

### Vorschlag als Dataclass
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Artifact:
    path: str
    content: str
    artifact_kind: str
```

### Bedeutung
Artifacts sind die transportierbaren Ergebnisse entlang der Operations.

---

## 2.6 StepResult
Das StepResult dokumentiert das Ergebnis eines Arbeitsgangs.

### Verantwortung
- Erfolg / Fehler
- Nachricht
- evtl. Metadaten

### Vorschlag als Dataclass
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class StepResult:
    operation: str
    success: bool
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
```

---

## 2.7 ProductionContext
Der ProductionContext ist der zentrale Zustand des Werkstücks während des Laufs.

### Verantwortung
Trägt alles, was zwischen Operations weitergegeben wird:
- Blueprint
- WorkOrder
- ProductionProfile
- generierte Dokumente
- extrahierte Files
- angewendete Dateien
- Prüfergebnisse
- Fehler
- Status

### Vorschlag als Dataclass
```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass
class ProductionContext:
    blueprint: Blueprint
    work_order: WorkOrder
    profile: ProductionProfile

    base_dir: Path | None = None
    prompt_text: str | None = None
    review_text: str | None = None
    response_text: str | None = None

    extracted_files: dict[str, str] = field(default_factory=dict)
    written_files: list[Path] = field(default_factory=list)

    step_results: list[StepResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_result(self, result: StepResult) -> None:
        self.step_results.append(result)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
```

### Bedeutung
Der Context ist das zentrale Transportmedium.
Er entspricht dem Werkstückzustand auf der Fertigungsstraße.

---

# 3. Machine-Modell

## Leitidee
Eine Machine ist eine technische Ausführungseinheit für genau einen Arbeitsschritt.

### Vorschlag als Basisklasse / Protocol
```python
from typing import Protocol

class Machine(Protocol):
    def run(self, context: ProductionContext) -> ProductionContext:
        ...
```

### Ziel
Damit lassen sich bestehende Komponenten später einheitlich anschließen:
- ValidatorMachine
- PromptBuilderMachine
- ReviewBuilderMachine
- RequestPackageWriterMachine
- ExecutorMachine
- OutputCheckerMachine
- OutputApplierMachine
- TestRunnerMachine

---

# 4. ProductionLine

Die ProductionLine orchestriert die Reihenfolge der Operations.

### Vorschlag
```python
from dataclasses import dataclass, field

@dataclass
class ProductionLine:
    machines: list[Machine] = field(default_factory=list)

    def run(self, context: ProductionContext) -> ProductionContext:
        for machine in self.machines:
            context = machine.run(context)
        return context
```

### Bedeutung
Die ProductionLine ist die lokale Orchestrierung der Vorproduktion.
Sie ist **nicht** die CI/CD-Pipeline.

---

# 5. Mapping auf euren aktuellen Stand

## Bereits vorhanden
Eure aktuellen Klassen entsprechen bereits grob diesen Rollen:

- `Validator` → ValidateOrder
- `PromptBuilder` → BuildPrompt
- `ReviewBuilder` → BuildReview
- `Writer` → WriteRequestPackage
- `Executor` → GenerateOutput
- `OutputChecker` → CheckOutputStructure
- `OutputApplier` → ApplyOutputFiles
- `TestRunner` → RunLocalTests

## Wichtig
Aktuell sind diese Klassen noch eher Step-Komponenten.
Der nächste Reifeschritt ist:
- gemeinsamer Context
- gemeinsames Zielmodell
- sauberer Orchestrator

---

# 6. Was wir ausdrücklich nicht tun

## Nicht Teil des lokalen Systems
- vollständige CI/CD nachbauen
- finale Freigabelogik
- Merge-Policies
- Deployment
- vollständige Integrationsstraße

## Warum?
Weil die eigentliche Fertigungsstraße in der CI/CD liegt.
Das lokale Tool ist Vorproduktion, Vorbereitung und strukturierte Übergabe.

---

# 7. Zielbild für den nächsten Umbau

## Schritt 1
Begriffe festziehen:
- Blueprint
- WorkOrder
- ProductionProfile
- ProductionContext
- StepResult

## Schritt 2
Bestehende Komponenten schrittweise auf `ProductionContext` umstellen

## Schritt 3
`main.py` von einem Demo-Skript in einen echten `ProductionLine`-Startpunkt überführen

## Schritt 4
später optionale Normalizer hinzufügen:
- Ruff
- Black
- Import-Sortierung

---

# 8. Empfehlung für den nächsten praktischen Umsetzungsschritt

Der nächste sinnvolle Codierungsschritt ist **nicht** sofort ein großer Umbau.
Sauberer ist:

1. `Blueprint`
2. `WorkOrder`
3. `ProductionProfile`
4. `ProductionContext`
5. `StepResult`

als neue Domain-Schicht einführen, **ohne** die bestehenden Maschinen sofort komplett umzuschreiben.

So bleibt der Umbau kontrolliert und deterministisch.

---

# 9. Zusammenfassung

## Fachliche Sicht
- Blueprint = Bauplan
- WorkOrder = Auftrag
- Operation = Arbeitsgang
- Machine = technische Station
- ProductionProfile = Kalibrierung
- Artifact = Werkstück
- ProductionContext = Werkstückzustand

## Systemgrenze
- lokales Tool = Vorproduktion + Vorprüfung
- CI/CD = eigentliche Fertigungsstraße
- Merge Request = formale Übergabe zur Prüfung

---

# 10. Nächster Umsetzungsschritt

Als Nächstes sollten wir auf Basis dieses Zielmodells die **erste kleine Domain-Schicht in Python** anlegen:
- `core/domain/blueprint.py`
- `core/domain/work_order.py`
- `core/domain/profile.py`
- `core/domain/context.py`
- `core/domain/result.py`

und danach gezielt den bestehenden Flow schrittweise daran anschließen.
