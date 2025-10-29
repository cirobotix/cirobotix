# cirobotix/arc42_extract.py
from __future__ import annotations
import re
import html
from typing import Dict, List, Iterable, Tuple, Optional


# -----------------------------
# Normalisierung & Utilities
# -----------------------------

_NUM_PREFIX = re.compile(r'^\s*\d+(?:\.\d+)*\s*')  # 4. / 10.2. / 1.1.3 etc.


def _norm(s: str) -> str:
    """
    Normalisiert Überschriften und Needles:
    - HTML-Entities unescapen (&ouml; -> ö)
    - Nummerierungspräfixe entfernen ("4. Lösungsstrategie" -> "Lösungsstrategie")
    - Whitespace kollabieren
    - Lowercase
    """
    s = html.unescape(s or "")
    s = _NUM_PREFIX.sub("", s)
    s = " ".join(s.split())
    return s.lower()


# -----------------------------
# Heading-Erkennung (Positionsbasiert)
# -----------------------------

# Findet JEDE Überschrift h1..h6 inkl. Level, raw-title und Match-Positionen
_H_TAG = re.compile(r'(?is)<h([1-6])[^>]*>(.*?)</h\1>')


def _find_all_headings(storage_html: str) -> List[dict]:
    headings: List[dict] = []
    for m in _H_TAG.finditer(storage_html or ""):
        level = int(m.group(1))
        inner = m.group(2) or ""
        # sichtbarer Titel (Tags raus), Entities NICHT entfernen (machen wir in _norm)
        title_raw = re.sub(r"(?is)<.*?>", "", inner).strip()
        headings.append({
            "level": level,
            "title_raw": title_raw,
            "start": m.start(),
            "end": m.end(),  # Ende des schließenden </hN>
        })
    return headings


def _slice_sections_semantic(storage_html: str) -> List[dict]:
    """
    Erzeugt "semantische" Abschnitte:
    Für jede Überschrift H_i: Content = HTML von (Ende H_i) bis zur nächsten Überschrift H_j
    mit level_j <= level_i. Existiert keine solche, dann bis zum Dokumentende.
    Unterüberschriften (höhere Levels) bleiben IM Abschnitt enthalten.
    """
    doc = storage_html or ""
    hs = _find_all_headings(doc)

    sections: List[dict] = []
    if not hs:
        # keine Headings: alles als intro
        sections.append({
            "level": 0,
            "title_raw": "intro",
            "content_html": doc.strip(),
        })
        return sections

    for i, h in enumerate(hs):
        this_level = h["level"]
        # Suche nächstes Heading mit Level <= this_level
        stop_at: Optional[int] = None
        for j in range(i + 1, len(hs)):
            if hs[j]["level"] <= this_level:
                stop_at = hs[j]["start"]
                break
        content_html = doc[h["end"]: stop_at].strip() if stop_at is not None else doc[h["end"] :].strip()
        sections.append({
            "level": this_level,
            "title_raw": h["title_raw"],
            "content_html": content_html,
        })
    return sections


# -----------------------------
# Section-Map Normalisierung
# -----------------------------

def _normalize_map(section_map: Dict[str, List[str]]) -> List[Tuple[str, List[str]]]:
    """
    Normalisiert die section_map für den Match-Vergleich über _norm.
    Rückgabe: Liste von (normalized_key, [needle_norm1, needle_norm2, ...])
    Die Reihenfolge bleibt erhalten (first-match wins).
    """
    out: List[Tuple[str, List[str]]] = []
    for norm_key, needles in section_map.items():
        needles_norm = [_norm(str(n)) for n in (needles or []) if str(n).strip()]
        out.append((str(norm_key).strip(), needles_norm))
    return out


# -----------------------------
# Hauptfunktion
# -----------------------------

def arc42_extract(
    storage_html: str,
    section_map: Dict[str, List[str]],
    *,
    # WICHTIG: Standardmäßig ALLE Level als Abschnitts-Header zulassen (mapping),
    # das Schneiden selbst berücksichtigt ohnehin alle Level für die Stop-Regel.
    heading_levels: Iterable[int] = (1, 2, 3, 4, 5, 6),
    max_chars_per_section: int = 10_000,
) -> Dict[str, str]:
    """
    Extrahiert arc42-Abschnitte aus Confluence-Storage-HTML anhand einer konfigurierbaren Section-Map.

    - storage_html: kompletter Storage-Body der Seite.
    - section_map: { normalized_key: [list_of_possible_heading_titles] }
      Beispiel: {"solution_strategy": ["Lösungsstrategie","Solution Strategy"], ...}
    - heading_levels: Welche H-Level dürfen als "Section-Heads" gemappt werden.
      (Das Schneiden der Blöcke nutzt IMMER alle Level für die korrekte Stop-Regel.)
    - max_chars_per_section: harte Trunkierung pro Abschnitt (HTML, nicht Text).

    Rückgabe: { normalized_key: html_snippet (gekürzt) }
    Für alle Keys in section_map ist mindestens ein Eintrag vorhanden (ggf. leere Zeichenkette).
    """
    # 1) Semantische Abschnitte bilden (korrekte Parent-/Child-Handhabung)
    sem_sections = _slice_sections_semantic(storage_html or "")

    # 2) Heading-Level-Filter für das Mapping (nicht fürs Schneiden!)
    allowed_levels = {int(h) for h in heading_levels}

    # 3) Normalisierte Map und Ergebnisgrundlage
    norm_map = _normalize_map(section_map)
    result: Dict[str, str] = {norm_key: "" for norm_key, _ in norm_map}

    # 4) Matching: Titel (normalisiert) → erster passender normalized_key (first-match wins)
    for sec in sem_sections:
        level = sec["level"]
        if allowed_levels and level not in allowed_levels:
            # nicht als Section-Head vorgesehen – aber der Content bleibt korrekt
            continue

        title_norm = _norm(sec["title_raw"])
        if not title_norm:
            continue

        for norm_key, needles_norm in norm_map:
            if not needles_norm:
                continue

            exact_hit = any(title_norm == needle for needle in needles_norm)
            partial_hit = any(needle in title_norm for needle in needles_norm)

            if exact_hit or partial_hit:
                if not result.get(norm_key):  # nur erstes Vorkommen übernehmen
                    result[norm_key] = (sec["content_html"] or "")[:max_chars_per_section]
                break  # nächsten Abschnitt prüfen

    return result


# -----------------------------
# Debug-Helfer
# -----------------------------

def list_headings(storage_html: str, heading_levels=(1, 2, 3, 4, 5, 6)):
    levels = "|".join(str(int(h)) for h in heading_levels)
    pat = re.compile(rf"(?i)<h(?:{levels})[^>]*>(.*?)</h(?:{levels})>", re.DOTALL)
    titles = []
    for m in pat.finditer(storage_html or ""):
        title = re.sub(r"(?i)<.*?>", "", m.group(1)).strip()
        if title:
            titles.append(title)
    return titles
