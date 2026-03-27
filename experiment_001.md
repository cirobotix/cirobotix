# Experiment 001 – Controlled AI Code Generation (Registry Class)

## Ziel

Ziel dieses Experiments war es, zu prüfen, ob ein klar definierter Werkstücktyp
durch ein strukturiertes KI-System reproduzierbar und in brauchbarer Qualität
erzeugt werden kann.

Der Fokus lag auf:
- Standardisierung
- Reproduzierbarkeit
- automatischer Qualitätsprüfung

---

## Hypothese

Ein enger Werkstücktyp in Kombination mit:
- strukturiertem Request
- klar definiertem Prompt
- und automatischer Validierung

führt zu kontrollierbarem und brauchbarem KI-Output.

---

## Werkstücktyp

**python_registry_class**

### Anforderungen

- genau eine Klasse
- Name: `ArtifactRegistry`
- Methoden:
  - `register(definition)`
  - `get(name)`
  - `list_names()`
- Verhalten:
  - `register`: erwartet Objekt mit `name: str`
  - `get`: wirft `KeyError` bei unbekanntem Namen
  - `list_names`: gibt sortierte Liste zurück
- Type Hints erforderlich
- Docstring erforderlich
- pytest-Testdatei erforderlich

---

## Systemaufbau

1. **Artifact Definition**
   - Definition des Werkstücktyps

2. **Request**
   - konkrete Parameter (class_name, paths, methods, Verhalten)

3. **Validate**
   - Prüfung der Eingabestruktur
   - Generierung von:
     - `task.json`
     - `prompt.md`
     - `review.md`

4. **Execute**
   - OpenAI API Call (LLM)

5. **Output**
   - strukturierte Rückgabe mit Dateimarkern

6. **Output Checker**
   - automatische Validierung:
     - Datei-Struktur
     - Klassendefinition
     - Methoden
     - Testdatei
     - pytest Nutzung

---

## Iterationen

### V1

- einfacher Prompt
- keine strukturierte Output-Anforderung
- kein Checker

**Ergebnis:**
- brauchbarer Code
- aber inkonsistente Struktur
- keine kontrollierte Validierung

---

### V2

- erweiterter Prompt mit:
  - klaren Verhaltensregeln
  - Dateipfaden
  - Output-Format
- erster Output Checker

**Ergebnis:**
- Output ähnlich zu V1
- Erkenntnis:
  - Prompt allein verbessert Output nicht signifikant

---

### V3 (entscheidender Schritt)

- Output Checker auf Dateibasis umgestellt
- Prüfung pro Werkstück (Source / Test getrennt)
- harte Validierungsregeln

**Ergebnis:**
- Check bestanden
- strukturierter Output
- reproduzierbarer Prozess

---

## Zentrale Erkenntnisse

### 1. Prompt Engineering ist nicht ausreichend

Verbesserte Prompts führen nicht automatisch zu besserem oder kontrollierbarem Output.

---

### 2. KI lässt sich nicht direkt steuern

Die KI optimiert auf:
- Plausibilität
- Einfachheit
- bekannte Muster

Nicht zwingend auf:
- exakte Anforderungen

---

### 3. Kontrolle entsteht durch Systemgrenzen

Qualität entsteht erst durch:
- Werkstückdefinition
- Constraints
- Output-Struktur
- nachgelagerte Validierung

---

### 4. Output-Validierung ist entscheidend

Der größte Qualitätshebel ist nicht der Prompt,
sondern die automatische Prüfung des Ergebnisses.

---

### 5. Werkstücktypen müssen eng geschnitten sein

Je enger der Werkstücktyp:
- desto weniger Interpretationsspielraum
- desto stabiler der Output

---

## Ergebnisbewertung

| Kriterium            | Bewertung |
|---------------------|----------|
| Funktionalität      | gut       |
| Struktur            | gut       |
| Reproduzierbarkeit  | vorhanden |
| Kontrollierbarkeit  | deutlich verbessert |
| Automatisierung     | teilweise |

---

## Fazit

Ein kontrollierter KI-gestützter Produktionsprozess ist möglich,
wenn die KI nicht direkt gesteuert wird, sondern durch ein System
aus Definition, Constraints und Validierung eingerahmt wird.

---

## Nächste Schritte

- Checker erweitern (strengere Regeln)
- weitere Werkstücktypen definieren
- Retry-Mechanismus bei fehlgeschlagenem Output
- Integration in CI/CD Pipeline