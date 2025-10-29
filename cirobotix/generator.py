# cirobotix/generator.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from html.parser import HTMLParser
import html as _html
import re
import datetime as dt


# --------------------------------------------------------------------------------------
# Minimaler HTML -> Markdown / Text Konverter (keine externen Libraries)
# --------------------------------------------------------------------------------------

class _HTML2Textish(HTMLParser):
    def __init__(self, as_markdown: bool = True):
        super().__init__(convert_charrefs=True)
        self.as_md = as_markdown
        self.buf: List[str] = []
        self._list_stack: List[str] = []
        self._in_pre = False
        self._in_code = False
        self._row_cells: List[str] = []
        self._in_row = False
        self._link_href_stack: List[str] = []

    def _w(self, s: str) -> None:
        if s:
            self.buf.append(s)

    def _nl(self, n: int = 1) -> None:
        if not self.buf or not self.buf[-1].endswith("\n"):
            self.buf.append("\n" * n)

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag in ("p", "div", "br"):
            self._nl()
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._nl(2)
            if self.as_md:
                level = int(tag[1])
                self._w("#" * level + " ")
        elif tag in ("ul", "ol"):
            self._list_stack.append(tag)
            self._nl()
        elif tag == "li":
            self._nl()
            if self._list_stack:
                bullet = "- " if self._list_stack[-1] == "ul" else "1. "
                self._w(bullet)
        elif tag in ("strong", "b"):
            if self.as_md: self._w("**")
        elif tag in ("em", "i"):
            if self.as_md: self._w("_")
        elif tag == "pre":
            self._nl(2)
            if self.as_md: self._w("```")
            self._nl()
            self._in_pre = True
        elif tag == "code":
            if not self._in_pre and self.as_md:
                self._w("`")
            self._in_code = True
        elif tag == "table":
            self._nl(2)
        elif tag == "tr":
            self._in_row = True
            self._row_cells = []
        elif tag == "hr":
            self._nl(2)
            self._w("---" if self.as_md else "----------------")
            self._nl(2)
        elif tag == "a":
            href = ""
            for k, v in attrs:
                if k.lower() == "href":
                    href = v or ""
                    break
            self._link_href_stack.append(href)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in ("p", "div"):
            self._nl()
        elif tag in ("ul", "ol"):
            if self._list_stack:
                self._list_stack.pop()
            self._nl()
        elif tag in ("strong", "b"):
            if self.as_md: self._w("**")
        elif tag in ("em", "i"):
            if self.as_md: self._w("_")
        elif tag == "code":
            if not self._in_pre and self.as_md:
                self._w("`")
            self._in_code = False
        elif tag == "pre":
            if self.as_md:
                if not (self.buf and self.buf[-1].endswith("\n")):
                    self._nl()
                self._w("```")
            self._nl(2)
            self._in_pre = False
        elif tag == "tr":
            if self._row_cells:
                line = " | ".join(c.strip() for c in self._row_cells)
                self._w(f"| {line} |" if self.as_md else line)
                self._nl()
            self._in_row = False
            self._row_cells = []
        elif tag == "a":
            href = self._link_href_stack.pop() if self._link_href_stack else ""
            if href and self.as_md:
                self._w(f" ({href})")

    def handle_data(self, data: str):
        if not data:
            return
        txt = _html.unescape(data)
        if self._in_row:
            self._row_cells.append(txt)
        else:
            self._w(txt)

    def get(self) -> str:
        out = "".join(self.buf)
        out = re.sub(r"\n{3,}", "\n\n", out).strip()
        return out


def html_to_markdown(s: str) -> str:
    p = _HTML2Textish(as_markdown=True)
    p.feed(s or "")
    return p.get()


def html_to_text(s: str) -> str:
    p = _HTML2Textish(as_markdown=False)
    p.feed(s or "")
    t = p.get()
    t = re.sub(r"[#*_`|]{1,}", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def convert_html(s: Optional[str], mode: str = "markdown") -> str:
    if not s:
        return ""
    if mode == "raw":
        return s
    if mode == "text":
        return html_to_text(s)
    return html_to_markdown(s)


# --------------------------------------------------------------------------------------
# Prompt Builder
# --------------------------------------------------------------------------------------

def _render_tech_stack(tech: Dict[str, Any]) -> str:
    lines: List[str] = []
    def add(title: str, items: list):
        if not items: return
        lines.append(f"### {title}")
        for it in items:
            if isinstance(it, dict):
                name = it.get("name", "")
                version = it.get("version")
                role = it.get("role")
                parts = [p for p in [name, version, f"· {role}" if role else None] if p]
                lines.append("- " + " ".join(parts))
            else:
                lines.append(f"- {it}")
        lines.append("")
    add("Languages", tech.get("languages", []))
    add("Frameworks", tech.get("frameworks", []))
    add("Data Stores", tech.get("data_stores", []))
    add("Testing", tech.get("testing", []))
    add("CI/CD", tech.get("ci_cd", []))
    if tech.get("constraints"):
        lines.append("### Constraints")
        for c in tech["constraints"]:
            lines.append(f"- {c}")
        lines.append("")
    if tech.get("notes"):
        lines.append("### Notes")
        for n in tech["notes"]:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines).strip()


def _pick_relevant_arc42(payload: Dict[str, Any], html_mode: str) -> str:
    arc = payload.get("arc42") or {}
    out: List[str] = []
    for title, key in [
        ("Goals", "goals"),
        ("Constraints", "constraints"),
        ("Context", "context"),
        ("Solution Strategy", "solution_strategy"),
        ("Building Blocks", "building_blocks"),
        ("Runtime View", "runtime_view"),
        ("Deployment View", "deployment_view"),
        ("Crosscutting", "crosscutting"),
        ("Quality Scenarios", "quality_scenarios"),
        ("Risks And Mitigations", "risks_and_mitigations"),
    ]:
        html = arc.get(key)
        if html:
            out.append(f"### {title}")
            out.append(convert_html(html, html_mode))
            out.append("")
    return "\n".join(out).strip()


def _pick_relevant_adrs(payload: Dict[str, Any], html_mode: str) -> str:
    adrs = payload.get("adrs") or []
    if not adrs:
        return ""
    out: List[str] = ["### Architekturentscheidungen (ADRs) – Auszüge"]
    for a in adrs:
        out.append(f"#### {a.get('title','ADR')}")
        out.append(convert_html(a.get("storage",""), html_mode))
        out.append("")
    return "\n".join(out).strip()


def build_plan_prompt(payload: Dict[str, Any], cfg: Dict[str, Any], html_mode: str = "markdown") -> str:
    app = (payload.get("meta") or {}).get("app", "unknown")
    tech = ((payload.get("metadata") or {}).get("tech_stack")) or {}
    ts = _render_tech_stack(tech)
    arc = _pick_relevant_arc42(payload, html_mode)
    adrs = _pick_relevant_adrs(payload, html_mode)
    now = dt.datetime.utcnow().isoformat() + "Z"
    return f"""# Planungs-Prompt für App: {app}

_Generated at: {now}_

Erzeuge auf Basis von Architektur (arc42) und ADRs einen **konkreten Umsetzungsplan** (Backlog → Epics → Stories → Tasks) für die nächste Iteration.
Fokussiere auf lieferbare Inkremente, Risiken und Abhängigkeiten. Berücksichtige den Tech-Stack.

## Tech Stack
{ts}

## Architektur (arc42) – relevante Auszüge
{arc}

## ADRs – relevante Auszüge
{adrs}
""".strip()


def _render_issue_block(issue: Dict[str, Any]) -> str:
    key = issue.get("key", "")
    summary = issue.get("summary", "")
    url = issue.get("url", "")
    desc = (issue.get("description") or "").strip()
    ac = issue.get("acceptance_criteria") or []

    lines = [f"### Ticket", f"- **Key**: {key}", f"- **Title**: {summary}"]
    if url: lines.append(f"- **URL**: {url}")
    if desc:
        lines.append("")
        lines.append("**Description**")
        lines.append("")
        lines.append(desc)
    if ac:
        lines.append("")
        lines.append("**Acceptance Criteria**")
        for i in ac:
            lines.append(f"- {i}")
    return "\n".join(lines).strip()


def _render_epic_block(issue: Dict[str, Any]) -> str:
    epic = issue.get("epic") or {}
    if not epic:
        return ""
    key = epic.get("key", "")
    summary = epic.get("summary", "")
    url = epic.get("url", "")
    desc = (epic.get("description") or "").strip()

    lines = ["### Epic", f"- **Key**: {key}", f"- **Title**: {summary}"]
    if url: lines.append(f"- **URL**: {url}")
    if desc:
        lines.append("")
        lines.append("**Epic Description**")
        lines.append("")
        lines.append(desc)
    return "\n".join(lines).strip()


def _render_scope_section(scope: str, allowed_paths: List[str], forbid_paths: List[str], base_setup: bool) -> str:
    lines: List[str] = []
    lines.append("## Scope & Boundaries")
    lines.append("")
    lines.append(f"- **Scope Mode**: `{scope}`")
    lines.append(f"- **Base Setup Allowed**: `{str(base_setup).lower()}`")
    if allowed_paths:
        lines.append("- **Allowed Paths** (create/modify):")
        for p in allowed_paths:
            lines.append(f"  - `{p}`")
    if forbid_paths:
        lines.append("- **Forbidden Paths** (do not create/modify):")
        for p in forbid_paths:
            lines.append(f"  - `{p}`")
    lines.append("")
    lines.append("**Change Policy**")
    lines.append("- Liefere **nur** die tatsächlich **geänderten/neu erstellten Dateien**.")
    lines.append("- **Kein** Projekt-Boilerplate, kein Global-Scaffold, keine Dummy-Dateien.")
    lines.append("- Erzeuge Migrations **nur**, wenn das Ticket DB-Änderungen erfordert.")
    lines.append("- Wenn ein benötigtes Prerequisite außerhalb der Allowed Paths liegt: "
                 "_stoppe Code-Erzeugung_, und liefere stattdessen einen kurzen Abschnitt "
                 "„Prerequisites & Minimal Manual Steps“ (ohne Fremd-Code).")
    lines.append("- Wenn `base_setup` false ist, nimm **keine** Änderungen an Projekt-Settings, WSGI/ASGI, manage.py etc. vor.")
    return "\n".join(lines).strip()


def build_implement_prompt_for_issue(
    payload: Dict[str, Any],
    issue: Dict[str, Any],
    html_mode: str = "markdown",
    *,
    scope: str = "ticket-only",
    allowed_paths: Optional[List[str]] = None,
    forbid_paths: Optional[List[str]] = None,
    base_setup: bool = False,
) -> str:
    """
    issue erwartet Felder: key, summary, url, description, acceptance_criteria[], epic{key,summary,url,description}
    """
    app = (payload.get("meta") or {}).get("app", "unknown")
    tech = ((payload.get("metadata") or {}).get("tech_stack")) or {}
    ts = _render_tech_stack(tech)
    arc = _pick_relevant_arc42(payload, html_mode)
    adrs = _pick_relevant_adrs(payload, html_mode)
    now = dt.datetime.utcnow().isoformat() + "Z"
    key = issue.get("key", "")
    ticket_block = _render_issue_block(issue)
    epic_block = _render_epic_block(issue)
    scope_block = _render_scope_section(scope, allowed_paths or [], forbid_paths or [], base_setup)

    return f"""# Implementierungs-Prompt für App: {app} — Ticket {key}

_Generated at: {now}_

## Ticket
{ticket_block}

{("" if not epic_block else "## Epic" + epic_block)}

{scope_block}

---

Richte dich strikt nach arc42/ADRs und dem metadata.tech_stack.
Liefere NUR:
1) Datei-Baum **nur der betroffenen Dateien** (ab Repo-Root)
2) Vollständige Datei-Inhalte **nur** für neue/geänderte Dateien (Codeblöcke mit Pfad-Kommentar: ```path: a/b/c```)
3) Tests (Unit/Integration) + Fixtures – **nur ticketrelevant**
4) DB-Migrationen (idempotent) – **nur wenn nötig**
5) Konfiguration (ENV), Logging, Healthcheck – **nur wenn vom Ticket gefordert**
6) Deploy/Makefile – **nur wenn durch das Ticket zwingend nötig**
7) Lint/Format/CI-Hinweise – **knapp, ticketbezogen**
8) Kurz-README – **nur die neuen/angepassten Kommandos**

**Constraints**
- Nutze Versionen/Technologien aus metadata.tech_stack.
- Keine Secrets – ENV-first. Deterministische Tests.
- Füge am Ende eine Conventional Commit Message hinzu.

## Kontext
### Tech Stack
{ts}

### Architektur (arc42) – relevante Auszüge
{arc}

### ADRs – relevante Auszüge
{adrs}
""".strip()
