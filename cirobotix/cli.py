# cirobotix/cli.py (stack-agnostic)
from __future__ import annotations

from typer import Typer, Option, Context
from rich import print
import json
from pathlib import Path
import datetime as dt
from typing import Any, Dict, List, Optional
import os

from cirobotix.confluence_client import (
    ConfluenceClient,
    extract_storage_html,
    page_title,
)
from cirobotix.arc42_extract import arc42_extract, list_headings
from cirobotix.config_loader import load_config, get_app_path, get_project_root, ConfigError
from cirobotix.generator import (
    build_plan_prompt,
    build_implement_prompt_for_issue,
)

# --- Jira (optional) ---
try:
    from cirobotix.jira_client import JiraClient
    from cirobotix.jira_ready_selector import find_epics_with_any_ready_children
    _JIRA_AVAILABLE = True
except Exception:
    JiraClient = None  # type: ignore
    find_epics_with_any_ready_children = None  # type: ignore
    _JIRA_AVAILABLE = False


app = Typer(help="Cirobotix CLI")


# -------------------------------
# Utility
# -------------------------------

def deep_merge(base: Any, override: Any) -> Any:
    if base is None:
        return override
    if override is None:
        return base
    if isinstance(base, dict) and isinstance(override, dict):
        res = dict(base)
        for k, v in override.items():
            if k in res and isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = deep_merge(res[k], v)
            else:
                res[k] = v
        return res
    return override


def _parse_ticket_list(s: str | None) -> List[str]:
    if not s:
        return []
    s = s.strip()
    if s == "*":
        return ["*"]
    return [x.strip() for x in s.split(",") if x.strip()]


def _normalize_jira_candidates(jira_summary: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    if not jira_summary:
        return []
    raw = jira_summary.get("candidates") or []
    out: List[Dict[str, Any]] = []

    for epic in raw:
        epic_key = epic.get("epic_key") or epic.get("key")
        epic_summary = epic.get("epic_summary") or epic.get("summary") or ""
        epic_url = epic.get("epic_url") or epic.get("url") or ""
        epic_desc = epic.get("epic_description") or epic.get("description") or ""

        if epic_key:
            out.append({
                "key": str(epic_key),
                "summary": str(epic_summary),
                "url": str(epic_url),
                "description": str(epic_desc),
                "acceptance_criteria": [],
                "epic": {
                    "key": str(epic_key),
                    "summary": str(epic_summary),
                    "url": str(epic_url),
                    "description": str(epic_desc),
                },
            })

        for ch in epic.get("ready_children", []) or []:
            issue = {
                "key": str(ch.get("key") or ""),
                "summary": str(ch.get("summary") or ""),
                "url": str(ch.get("url") or ""),
                "description": str(ch.get("description") or ""),
                "acceptance_criteria": list(ch.get("acceptance_criteria") or []),
                "epic": {
                    "key": str(epic_key or ""),
                    "summary": str(epic_summary or ""),
                    "url": str(epic_url or ""),
                    "description": str(epic_desc or ""),
                },
            }
            if issue["key"]:
                out.append(issue)

    # Dedupe by key
    seen = {}
    for it in out:
        seen[it["key"]] = it
    return list(seen.values())


def _guess_app_dir(cfg: Dict[str, Any], app_name: str) -> Path:
    """
    Try to determine the app directory without hard-coding a framework.
    Priority:
      1) Configured (get_app_path)
      2) Heuristics relative to project_root
      3) Fallback: apps/<app>
    """
    root = get_project_root(cfg)
    try:
        return get_app_path(cfg, app_name)
    except Exception:
        pass

    candidates = [
        root / "apps" / app_name,
        root / app_name,
        root / "src" / app_name,
        root / "backend" / app_name,
        root / "modules" / app_name,
        root / "packages" / app_name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # Fallback without existence check


def _parse_allow_list(s: str | None) -> List[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


# -------------------------------
# Stack profiles (configurable)
# -------------------------------

def _resolve_effective_stack(cfg: Dict[str, Any], app_name: str) -> Dict[str, Any]:
    """
    Merge global tech_stack with app-specific tech_stack overrides (if present).
    """
    global_stack = (cfg.get("tech_stack") or {})
    app_overrides = ((cfg.get("apps") or {}).get(app_name) or {})
    app_stack = (app_overrides.get("tech_stack") or {})
    return deep_merge(global_stack, app_stack) if (global_stack or app_stack) else {}


def _derive_stack_name(effective_stack: Dict[str, Any], explicit_stack: Optional[str]) -> str:
    """
    Decide the stack profile name.
    Priority: CLI --stack > effective_stack["name"] > default "django"
    """
    if explicit_stack:
        return explicit_stack.strip().lower()
    name = (effective_stack.get("name") or "").strip().lower()
    return name or "django"  # keep backward-compatible default


def _default_allowed_paths_for_profile(profile: str, app_dir: Path, project_root: Path) -> List[str]:
    """
    Allowed paths used when --scope=ticket-only and no --allow was provided.
    Return POSIX-like strings relative to project_root where possible.
    """
    def _rel(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(project_root.resolve())).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")

    # Canonicals for known stacks; extend as needed
    if profile in ("django", "django-rest", "python-django"):
        # previous behavior preserved
        base = _rel(app_dir)
        return [
            f"{base}/models.py",
            f"{base}/migrations/",
            f"{base}/tests/",
            f"{base}/admin.py",
            f"{base}/serializers.py",
            f"{base}/views.py",
            f"{base}/urls.py",
            f"{base}/schemas.py",
            f"{base}/selectors.py",
            f"{base}/services.py",
            f"{base}/forms.py",
            f"{base}/fixtures/",
        ]

    if profile in ("java-selenium", "selenium-java", "qa-selenium"):
        # typical Maven layout
        base = project_root  # Selenium tests often span multiple packages
        candidates = [
            "src/test/java/",
            "src/test/resources/",
            "src/main/resources/",
            "pom.xml",
            "build.gradle",
            "gradle.properties",
        ]
        return candidates

    if profile in ("generic", "plain"):
        # minimal, non-opinionated
        base = _rel(app_dir)
        return [
            f"{base}/",
            "README.md",
            "docs/",
            "tests/",
        ]

    # Fallback: behave like generic
    base = _rel(app_dir)
    return [
        f"{base}/",
        "README.md",
        "docs/",
        "tests/",
    ]


# -------------------------------
# Core execution
# -------------------------------

def _run_conf_fetch(
    *,
    project_config: str,
    app_name: str,
    out: str,
    debug: bool,
    include_jira: bool,
    mode: str,
    tickets: str,
    print_prompt: bool,
    html_mode: str,
    scope: str,
    allow: str,
    base_setup: bool,
    stack: Optional[str],
) -> None:
    if html_mode not in ("markdown", "text", "raw"):
        print(f"[red]Invalid --html-mode '{html_mode}'. Use: markdown | text | raw[/]")
        return
    if scope not in ("ticket-only", "epic", "project"):
        print(f"[red]Invalid --scope '{scope}'. Use: ticket-only | epic | project[/]")
        return

    cfg = load_config(project_config)

    # -------------------------------------------------------------------------
    # Confluence
    # -------------------------------------------------------------------------
    conf = cfg["confluence"]
    arc42_cfg = conf.get("arc42", {}) or {}
    section_map = arc42_cfg.get("section_map", {}) or {}
    heading_levels = arc42_cfg.get("heading_levels", [2, 3])
    max_chars_per_section = int(arc42_cfg.get("max_chars_per_section", 10_000))

    adr_cfg = conf.get("adr", {}) or {}
    adr_max_items = int(adr_cfg.get("max_items", 10))
    adr_max_chars = int(adr_cfg.get("max_chars", 2_000))

    app_label = f'{conf["labels"]["app_prefix"]}{app_name}'

    client = ConfluenceClient(
        base_url=conf["base_url"],
        email_env=conf.get("email_env", "CONFLUENCE_EMAIL"),
        token_env=conf.get("token_env", "CONFLUENCE_TOKEN"),
    )

    arc42_page = client.fetch_arc42_for_app(
        space=conf["space"],
        app_label=app_label,
        arc42_label=conf["labels"]["arc42"],
    )
    adrs = client.fetch_adrs_for_app(
        space=conf["space"],
        app_label=app_label,
        adr_label=conf["labels"]["adr"],
        max_items=adr_max_items,
    )

    arc42_html = extract_storage_html(arc42_page) if arc42_page else ""
    if debug:
        titles = list_headings(arc42_html, heading_levels=heading_levels)
        print(f"[yellow]Found {len(titles)} headings at levels {heading_levels}:[/]")
        for t in titles[:30]:
            print(f"  - {t}")

    arc42_sections = arc42_extract(
        storage_html=arc42_html,
        section_map=section_map,
        heading_levels=heading_levels,
        max_chars_per_section=max_chars_per_section,
    )

    adr_items = []
    for p in adrs:
        storage = extract_storage_html(p)
        adr_items.append({"title": page_title(p), "storage": (storage or "")[:adr_max_chars]})

    # -------------------------------------------------------------------------
    # Jira (optional)
    # -------------------------------------------------------------------------
    jira_summary = None
    if include_jira:
        if not _JIRA_AVAILABLE:
            print("[yellow]Jira modules not available – skipping Jira enrichment.[/]")
        else:
            jira_cfg = (cfg.get("jira") or {})
            try:
                jira_client = JiraClient(
                    base_url=jira_cfg["base_url"],
                    email_env=jira_cfg.get("email_env", "JIRA_EMAIL"),
                    token_env=jira_cfg.get("token_env", "JIRA_TOKEN"),
                )
                epic_candidates = find_epics_with_any_ready_children(jira_client, cfg)
                jira_summary = {
                    "project_key": jira_cfg.get("project_key"),
                    "project_mode": jira_cfg.get("project_mode", "auto"),
                    "ready_status": jira_cfg.get("ready_status", "READY FOR GENERATE"),
                    "candidates": epic_candidates,
                }
            except Exception as e:
                print(f"[red]Jira enrichment failed:[/] {e!r}")

    # -------------------------------------------------------------------------
    # Tech-Stack (global + App-Override + CLI override)
    # -------------------------------------------------------------------------
    effective_stack = _resolve_effective_stack(cfg, app_name)
    profile_name = _derive_stack_name(effective_stack, stack)

    # -------------------------------------------------------------------------
    # Payload
    # -------------------------------------------------------------------------
    payload = {
        "meta": {
            "app": app_name,
            "generated_at": dt.datetime.utcnow().isoformat() + "Z",
            "config": {
                "arc42": {
                    "heading_levels": heading_levels,
                    "max_chars_per_section": max_chars_per_section,
                    "mapped_sections": list(section_map.keys()),
                },
                "adr": {"max_items": adr_max_items, "max_chars": adr_max_chars},
                "jira": {
                    **({"project_key": (cfg.get("jira") or {}).get("project_key")} if cfg.get("jira") else {}),
                    **({"project_mode": (cfg.get("jira") or {}).get("project_mode", "auto")} if cfg.get("jira") else {}),
                    **({"ready_status": (cfg.get("jira") or {}).get("ready_status", "READY FOR GENERATE")} if cfg.get("jira") else {}),
                },
            },
        },
        "metadata": {
            "tech_stack": {
                **effective_stack,
                "profile": profile_name,  # normalized profile name
            }
        },
        "arc42": arc42_sections,
        "adrs": adr_items,
        "raw": {
            "arc42_title": page_title(arc42_page) if arc42_page else None,
            "arc42_storage_len": len(arc42_html),
            "adr_count": len(adr_items),
        },
    }
    if jira_summary is not None:
        payload["jira"] = jira_summary

    # Persist context JSON
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Prompt generation
    if mode not in ("plan", "implement"):
        print(f"[red]Unknown --mode '{mode}'. Use 'plan' or 'implement'.[/]")
        return

    if mode == "plan":
        if print_prompt:
            prompt = build_plan_prompt(payload, cfg, html_mode=html_mode)
            print("\n[bold cyan]=== GENERATED PLAN PROMPT ===[/bold cyan]\n")
            print(prompt)
            print("\n[bold cyan]=== END PLAN PROMPT ===[/bold cyan]\n")
    else:
        keys = _parse_ticket_list(tickets)
        norm = _normalize_jira_candidates(payload.get("jira"))
        if keys == ["*"]:
            keys = [c["key"] for c in norm]
        if not keys and norm:
            keys = [c["key"] for c in norm]

        if not keys:
            print("[yellow]No tickets specified and no Jira candidates found. Nothing to implement.[/]")
        else:
            project_root = get_project_root(cfg)
            app_dir = _guess_app_dir(cfg, app_name)

            # Allowed/Forbid Paths
            default_allowed = (
                _default_allowed_paths_for_profile(profile_name, app_dir, project_root)
                if scope == "ticket-only" else []
            )
            extra_allowed = _parse_allow_list(allow)
            allowed_paths = default_allowed + extra_allowed
            forbid_paths: List[str] = []  # keep free for future profile-specific forbids

            by_key = {c["key"]: c for c in norm}
            if print_prompt and keys:
                print(f"[blue]Resolved tickets:[/] {', '.join(keys)}")
            for k in keys:
                issue = by_key.get(k)
                if not issue:
                    print(f"[yellow]Ticket '{k}' not found among Jira candidates – skipping.[/]")
                    continue
                prompt = build_implement_prompt_for_issue(
                    payload,
                    issue,
                    html_mode=html_mode,
                    scope=scope,
                    allowed_paths=allowed_paths,
                    forbid_paths=forbid_paths,
                    base_setup=base_setup,
                )
                if print_prompt:
                    print(f"\n[bold cyan]=== GENERATED IMPLEMENT PROMPT: {k} ===[/bold cyan]\n")
                    print(prompt)
                    print(f"\n[bold cyan]=== END PROMPT: {k} ===[/bold cyan]\n")

    mapped = ", ".join(k for k, v in arc42_sections.items() if v)
    jira_ready = len(_normalize_jira_candidates(payload.get("jira"))) if payload.get("jira") else 0
    has_stack = "yes" if effective_stack else "no"
    print(
        f"[green]Confluence fetched[/] for app '[bold]{app_name}[/]': "
        f"arc42_title=[italic]{payload['raw']['arc42_title']}[/], "
        f"sections_mapped=[{mapped or 'none'}], "
        f"adrs={payload['raw']['adr_count']}, "
        f"tech_stack={has_stack} (profile='{profile_name}'), "
        f"jira_ready_tickets={jira_ready} "
        f"→ {out}"
    )


# -------------------------------
# Typer entry points
# -------------------------------

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    project_config: str = Option("docs/cirobotix.project.yaml", "--project-config", "-c"),
    app_name: str = Option(..., "--app", "-a", help="Application key/name (framework-agnostic)"),
    out: str = Option("cirobotix/context/_conf_sample.json", "--out"),
    debug: bool = Option(False, "--debug", help="Print parsed headings for arc42 page"),
    include_jira: bool = Option(True, "--include-jira/--no-include-jira", help="Include Jira EPIC/ticket candidates"),
    mode: str = Option("plan", "--mode", help="plan | implement"),
    tickets: str = Option("", "--tickets", help="Comma-separated ticket keys, e.g. 'SMP-1,SMP-2' or '*'"),
    print_prompt: bool = Option(True, "--print-prompt/--no-print-prompt", help="Print generated prompts"),
    html_mode: str = Option("markdown", "--html-mode", help="markdown | text | raw"),
    scope: str = Option("ticket-only", "--scope", help="ticket-only | epic | project"),
    allow: str = Option("", "--allow", help="Extra allowed paths (comma-separated)"),
    base_setup: bool = Option(False, "--base-setup/--no-base-setup", help="Allow minimal project bootstrap if missing"),
    stack: Optional[str] = Option(None, "--stack", help="Override stack profile (e.g., 'django', 'java-selenium', 'generic')"),
):
    if ctx.invoked_subcommand is not None:
        return
    _run_conf_fetch(
        project_config=project_config,
        app_name=app_name,
        out=out,
        debug=debug,
        include_jira=include_jira,
        mode=mode,
        tickets=tickets,
        print_prompt=print_prompt,
        html_mode=html_mode,
        scope=scope,
        allow=allow,
        base_setup=base_setup,
        stack=stack,
    )


@app.command("conf-fetch")
def conf_fetch(
    project_config: str = Option("docs/cirobotix.project.yaml", "--project-config", "-c"),
    app_name: str = Option(..., "--app", "-a", help="Application key/name (framework-agnostic)"),
    out: str = Option("cirobotix/context/_conf_sample.json", "--out"),
    debug: bool = Option(False, "--debug", help="Print parsed headings for arc42 page"),
    include_jira: bool = Option(True, "--include-jira/--no-include-jira", help="Include Jira EPIC/ticket candidates"),
    mode: str = Option("plan", "--mode", help="plan | implement"),
    tickets: str = Option("", "--tickets", help="Comma-separated ticket keys, e.g. 'SMP-1,SMP-2' or '*'"),
    print_prompt: bool = Option(True, "--print-prompt/--no-print-prompt", help="Print generated prompts"),
    html_mode: str = Option("markdown", "--html-mode", help="markdown | text | raw"),
    scope: str = Option("ticket-only", "--scope", help="ticket-only | epic | project"),
    allow: str = Option("", "--allow", help="Extra allowed paths (comma-separated)"),
    base_setup: bool = Option(False, "--base-setup/--no-base-setup", help="Allow minimal project bootstrap if missing"),
    stack: Optional[str] = Option(None, "--stack", help="Override stack profile (e.g., 'django', 'java-selenium', 'generic')"),
):
    _run_conf_fetch(
        project_config=project_config,
        app_name=app_name,
        out=out,
        debug=debug,
        include_jira=include_jira,
        mode=mode,
        tickets=tickets,
        print_prompt=print_prompt,
        html_mode=html_mode,
        scope=scope,
        allow=allow,
        base_setup=base_setup,
        stack=stack,
    )


if __name__ == "__main__":
    app()
