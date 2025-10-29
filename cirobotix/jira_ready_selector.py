from __future__ import annotations
import itertools
import re
from typing import Dict, List, Iterable, Tuple, Optional, Any

# Erwartete Jira-Client API:
# jira.search(jql, startAt=0, maxResults=50, fields=None) -> dict
# jira.get_project(key) -> dict
# jira.get_fields() -> List[dict]


# -------------------------------
# Helpers
# -------------------------------

def _chunked(seq: List[str], n: int) -> Iterable[List[str]]:
    it = iter(seq)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def _resolve_mode(jira, project_key: str, cfg_mode: str) -> str:
    """Bestimmt automatisch: company vs team-managed."""
    if cfg_mode in ("company", "team"):
        return cfg_mode
    info = jira.get_project(project_key)
    return "team" if bool(info.get("simplified")) else "company"


def _resolve_field_id_map(jira, configured_names: Dict[str, str] | None) -> Dict[str, str]:
    """Mappt logische Feldnamen auf Jira-Feld-IDs (case-insensitiv)."""
    out: Dict[str, str] = {}
    if not configured_names:
        return out
    wanted = { (v or "").strip().lower(): k for k, v in configured_names.items() if isinstance(v, str) and v.strip() }
    if not wanted:
        return out
    for f in jira.get_fields():
        name = (f.get("name") or "").strip().lower()
        if name in wanted:
            out[wanted[name]] = f.get("id")
    return out


def _resolve_epic_link_field_id(jira, configured: str | None) -> Optional[str]:
    """Ermittelt die ID des Felds 'Epic Link'."""
    if configured:
        return configured
    for f in jira.get_fields():
        if (f.get("name") or "").strip().lower() == "epic link":
            return f.get("id")
    return None


# ---------- ADF (Atlassian Document Format) -> Plain Text ----------

def _adf_to_text(node: Any) -> str:
    """Konvertiert Jira ADF (dict/list/str) robust in Plaintext."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "\n".join(filter(None, (_adf_to_text(n) for n in node))).strip()
    if isinstance(node, dict):
        parts: List[str] = []
        if isinstance(node.get("text"), str):
            parts.append(node["text"])
        content = node.get("content")
        if isinstance(content, list):
            sub = "\n".join(_adf_to_text(c) for c in content if c)
            if sub.strip():
                parts.append(sub)
        return "\n".join(parts).strip()
    return str(node)


def _to_text(val: Any) -> str:
    """Akzeptiert String/ADF/Listen und liefert sauberen Text."""
    return _adf_to_text(val).strip()


# -------------------------------
# Sanitizer (Umbruch-Korrektur)
# -------------------------------

def _sanitize_wrapped_text(text: str) -> str:
    """Glättet weiche Umbrüche aus Confluence/Jira-ADF ohne Listen zu zerstören."""
    if not text:
        return ""

    # 1) Normalisieren
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)

    # 2) Komma/Doppelpunkt-Umbrüche glätten
    text = re.sub(r',\n\s+', ', ', text)
    text = re.sub(r':\n\s+', ': ', text)

    # 3) Blockweise unwrappen (Nicht-Listenblöcke)
    blocks = re.split(r'\n{2,}', text)
    fixed_blocks = []
    for b in blocks:
        # Ist es eine Liste?
        is_list = any(re.match(r'^\s*(?:[-*+]|(\d+\.))\s+', ln) for ln in b.splitlines() if ln.strip())
        if not is_list:
            # Einzellinien-Umbrüche in Fließtext entfernen
            b = re.sub(
                r'(?<![.!?:;)\]”»\-])\n(?!\s*\n|[-*+]\s|\d+\.\s|#+\s)',
                ' ',
                b
            )
        fixed_blocks.append(b)

    text = '\n\n'.join(fixed_blocks)

    # 4) Feinschliff
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[ \t]+\n', '\n', text)

    return text.strip()


def _normalize_text(val: Any) -> str:
    """ADF/Listen -> Plaintext + Sanitizer (Umbruch-/Kommafix)."""
    return _sanitize_wrapped_text(_to_text(val))


def _split_acceptance_criteria(val: Any) -> List[str]:
    """Extrahiert Akzeptanzkriterien aus String/ADF/Listen."""
    text = _to_text(val)
    if not text:
        return []
    text = _sanitize_wrapped_text(text)
    lines_raw = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out: List[str] = []
    for raw in lines_raw:
        s = raw.lstrip("-*•+–—\t ").lstrip("0123456789. ").strip()
        if len(s) >= 3:
            out.append(" ".join(s.split()))
    # Fallback: Trennung über Komma, Semikolon oder Punkt-Aufzählungen
    if not out and any(ch in text for ch in (";", "·", ",")):
        tmp = text.replace("·", ";")
        for chunk in re.split(r'[;,]', tmp):
            s = chunk.strip()
            if len(s) >= 3:
                out.append(" ".join(s.split()))
    return out


# -------------------------------
# Search helpers
# -------------------------------

def _search_all(jira, jql: str, page_size: int = 100, fields: Optional[List[str]] = None) -> List[dict]:
    """Paginierte Suche mit automatischer Zusammenführung."""
    start, out = 0, []
    while True:
        resp = jira.search(jql, startAt=start, maxResults=page_size, fields=fields)
        issues = resp.get("issues", [])
        out.extend(issues)
        if start + len(issues) >= resp.get("total", 0) or not issues:
            break
        start += len(issues)
    return out


# -------------------------------
# Company vs Team grouping
# -------------------------------

def _children_group_by_epic_company(
    jira, project_key: str, epic_keys: List[str],
    ready_status: str, epic_link_field_id: str,
    page_size: int, child_field_ids: List[str]
) -> Dict[str, List[dict]]:
    """Ordnet Company-Managed Tickets nach 'Epic Link'."""
    groups: Dict[str, List[dict]] = {k: [] for k in epic_keys}
    if not epic_keys:
        return groups
    base_fields = ["key", "summary", "status", "description", epic_link_field_id]
    req_fields = list({*base_fields, *child_field_ids})
    for chunk in _chunked(epic_keys, 1000):
        in_list = ",".join(chunk)
        jql = (
            f'project = {project_key} AND status = "{ready_status}" '
            f'AND "Epic Link" in ({in_list}) ORDER BY key'
        )
        issues = _search_all(jira, jql, page_size=page_size, fields=req_fields)
        for it in issues:
            epic_link = it.get("fields", {}).get(epic_link_field_id) or {}
            epic_key = epic_link.get("key")
            if epic_key:
                groups.setdefault(epic_key, []).append(it)
    return groups


def _children_group_by_epic_team(
    jira, project_key: str, epic_keys: List[str],
    ready_status: str, page_size: int, child_field_ids: List[str]
) -> Dict[str, List[dict]]:
    """Ordnet Team-Managed Tickets nach 'parent'."""
    groups: Dict[str, List[dict]] = {k: [] for k in epic_keys}
    if not epic_keys:
        return groups
    base_fields = ["key", "summary", "status", "description", "parent"]
    req_fields = list({*base_fields, *child_field_ids})
    for chunk in _chunked(epic_keys, 1000):
        in_list = ",".join(chunk)
        jql = (
            f'project = {project_key} AND status = "{ready_status}" '
            f'AND parent in ({in_list}) ORDER BY key'
        )
        issues = _search_all(jira, jql, page_size=page_size, fields=req_fields)
        for it in issues:
            parent = it.get("fields", {}).get("parent") or {}
            epic_key = parent.get("key")
            if epic_key:
                groups.setdefault(epic_key, []).append(it)
    return groups


# -------------------------------
# Main function
# -------------------------------

def find_epics_with_any_ready_children(jira, config: Dict) -> List[Dict]:
    """
    Liefert alle EPICs im Status READY FOR GENERATE mit >=1 Child im selben Status.
    Enthält vollständigen EPIC-Kontext (Beschreibung, Felder, URL) und Kinder mit Details.
    """
    jira_cfg = config.get("jira") or {}
    proj = jira_cfg["project_key"]
    ready = jira_cfg.get("ready_status", "READY FOR GENERATE")
    page_size = int(jira_cfg.get("page_size", 100))
    mode = _resolve_mode(jira, proj, jira_cfg.get("project_mode", "auto"))

    # 1) Custom-Feld-IDs auflösen
    custom_name_map = (jira_cfg.get("fields") or {})
    logical_to_id = _resolve_field_id_map(jira, custom_name_map)
    child_field_ids: List[str] = list(logical_to_id.values())

    # 2) EPIC-Kandidaten (inkl. Beschreibung)
    epics_jql = f'project = {proj} AND issuetype = Epic AND status = "{ready}" ORDER BY key'
    epics = _search_all(jira, epics_jql, page_size=page_size, fields=["key", "summary", "status", "description"])
    epic_keys = [e["key"] for e in epics]
    if not epic_keys:
        return []

    # 3) READY-Kinder gruppieren
    if mode == "company":
        epic_link_field_id = _resolve_epic_link_field_id(jira, jira_cfg.get("epic_link_field", ""))
        if not epic_link_field_id:
            raise RuntimeError('Epic Link field id not found. Set jira.epic_link_field (e.g. "customfield_10014").')
        groups = _children_group_by_epic_company(
            jira, proj, epic_keys, ready, epic_link_field_id, page_size, child_field_ids
        )
    else:
        groups = _children_group_by_epic_team(
            jira, proj, epic_keys, ready, page_size, child_field_ids
        )

    # Helper zum Mappen der logischen Felder
    def _logical_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for logical, fid in logical_to_id.items():
            val = fields.get(fid)
            if isinstance(val, list):
                out[logical] = [
                    _normalize_text(v if isinstance(v, str) else (v.get("value") or v.get("name") or v))
                    for v in val
                ]
            elif isinstance(val, dict):
                out[logical] = _normalize_text(val.get("value") or val.get("name") or val.get("text") or val)
            else:
                out[logical] = val if isinstance(val, (int, float)) else _normalize_text(val)
        if "acceptance_criteria" in out:
            out["acceptance_criteria"] = _split_acceptance_criteria(out["acceptance_criteria"])
        return out

    # 4) Ergebnis aufbauen
    result: List[Dict] = []
    base = getattr(jira, "base_url", "").rstrip("/")

    for e in epics:
        epic_key = e["key"]
        epic_summary = e.get("fields", {}).get("summary")
        epic_desc = _normalize_text(e.get("fields", {}).get("description"))
        epic_url = f"{base}/browse/{epic_key}" if base else None

        kids = groups.get(epic_key, [])
        if not kids:
            continue

        epic_fields = _logical_fields(e.get("fields", {})) if logical_to_id else {}

        result.append({
            "epic_key": epic_key,
            "epic_summary": epic_summary,
            "epic_url": epic_url,
            "epic_description": epic_desc,
            "ready_children": [
                {
                    "key": k["key"],
                    "url": f"{base}/browse/{k['key']}" if base else None,
                    "summary": k["fields"].get("summary"),
                    "description": _normalize_text(
                        k["fields"].get("description")),
                    "status": k["fields"]["status"]["name"],
                    "status_lc": k["fields"]["status"]["name"].strip().lower(),
                    "epic": {
                        "key": epic_key,
                        "summary": epic_summary,
                        "url": epic_url,
                    },
                    **_logical_fields(k.get("fields", {}))
                }
                for k in kids
            ],
        })

    return result
