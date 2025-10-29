# cirobotix/config_loader.py
from __future__ import annotations

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Union

import yaml


_JSON_TYPES = (dict, list, str, int, float, bool, type(None))
_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::([^}]*))?\}")  # ${VAR[:default]}


class ConfigError(ValueError):
    """Konfigurationsfehler mit klarer Nachricht."""
    pass


def _read_yaml(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"Top-level YAML muss ein Mapping sein: {path}")
        return data
    except FileNotFoundError:
        raise ConfigError(f"Config-Datei nicht gefunden: {path}")
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML-Fehler in {path}: {e}") from e


def _interpolate_env_in_str(s: str) -> str:
    """
    Ersetzt ${VARNAME[:default]} durch Umgebungsvariablen.
    Beispiel:
      - "https://${HOST}/wiki"  (wenn HOST gesetzt)
      - "${TOKEN:changeme}"     (Default, falls nicht gesetzt)
    """
    def repl(m: re.Match) -> str:
        var, default = m.group(1), m.group(2)
        val = os.getenv(var, default if default is not None else "")
        return val
    return _ENV_PATTERN.sub(repl, s)


def _interpolate_env(obj: Any) -> Any:
    """Wendet _interpolate_env_in_str rekursiv auf Strings in JSON-ähnlichen Strukturen an."""
    if isinstance(obj, str):
        return _interpolate_env_in_str(obj)
    if isinstance(obj, list):
        return [_interpolate_env(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _interpolate_env(v) for k, v in obj.items()}
    return obj


def _deep_get(d: Mapping[str, Any], path: Iterable[str], default: Any = None) -> Any:
    cur: Any = d
    for p in path:
        if not isinstance(cur, Mapping) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _deep_setdefault(d: MutableMapping[str, Any], path: Iterable[str], value: Any) -> None:
    cur: MutableMapping[str, Any] = d
    segs = list(path)
    for p in segs[:-1]:
        nxt = cur.get(p)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[p] = nxt
        cur = nxt  # type: ignore
    cur.setdefault(segs[-1], value)


def _apply_defaults(cfg: dict, config_dir: Path) -> None:
    """
    Setzt behutsam Defaults, ohne vorhandene Werte zu überschreiben.
    """
    # Projekt-Root = Ordner der Konfig, falls nicht explizit angegeben
    _deep_setdefault(cfg, ("project", "name"), "Cirobotix Project")
    _deep_setdefault(cfg, ("project", "monorepo_root"), str(config_dir))

    # Globaler Tech-Stack & Apps-Container (für optionale App-Overrides)
    _deep_setdefault(cfg, ("tech_stack",), {})  # globaler Standard-Stack
    _deep_setdefault(cfg, ("apps",), {})        # optionale App-spezifische Konfigurationen

    # Confluence: arc42-Defaults
    _deep_setdefault(cfg, ("confluence", "arc42", "section_map"), {
        "solution_strategy": ["Lösungsstrategie", "Solution Strategy"],
        "building_blocks": ["Bausteinsicht", "Building Block View"],
        "crosscutting": ["Querschnittliche Konzepte", "Crosscutting"],
        "constraints": ["Randbedingungen", "Constraints"],
        "goals": ["Ziele", "Goals"],
    })
    _deep_setdefault(cfg, ("confluence", "arc42", "heading_levels"), [2, 3])
    _deep_setdefault(cfg, ("confluence", "arc42", "max_chars_per_section"), 10_000)

    # Confluence: ADR-Defaults
    _deep_setdefault(cfg, ("confluence", "adr", "max_items"), 10)
    _deep_setdefault(cfg, ("confluence", "adr", "max_chars"), 2_000)

    # Context-Budget generisch
    _deep_setdefault(cfg, ("context_budget", "max_chars_total"), 24_000)
    _deep_setdefault(cfg, ("context_budget", "max_chars_confluence"), 10_000)
    _deep_setdefault(cfg, ("context_budget", "max_chars_repo"), 9_000)
    _deep_setdefault(cfg, ("context_budget", "max_chars_jira"), 3_000)
    _deep_setdefault(cfg, ("context_budget", "max_chars_epic"), 2_000)


def _validate_required(cfg: dict) -> None:
    """
    Prüft, ob für den aktuellen MVP die minimal nötigen Keys vorhanden sind.
    Wir validieren schrittweise: Confluence-Client wird zuerst verwendet.
    """
    # confluence
    c = cfg.get("confluence")
    if not isinstance(c, dict):
        raise ConfigError("Fehlender Abschnitt 'confluence' in der Config.")

    for key in ("base_url", "space", "labels"):
        if key not in c:
            raise ConfigError(f"confluence.{key} fehlt in der Config.")

    labels = c.get("labels")
    if not isinstance(labels, dict):
        raise ConfigError("confluence.labels muss ein Mapping sein.")

    for key in ("arc42", "adr", "app_prefix"):
        if key not in labels:
            raise ConfigError(f"confluence.labels.{key} fehlt in der Config.")

    # Optional, aber häufig sinnvoll
    # django.apps Mapping
    django = cfg.get("django", {})
    if django and not isinstance(_deep_get(django, ("apps",), {}), dict):
        raise ConfigError("django.apps muss ein Mapping {app_name: path} sein, wenn gesetzt.")

    # Hinweis zu env vars (nur Info, keine harte Validierung hier)
    # Auth wird zur Laufzeit im Client geprüft.


def _resolve_paths_relative_to_config(cfg: dict, config_dir: Path) -> None:
    """
    Löst ausgewählte Pfade relativ zum Speicherort der Config-Datei auf.
    """
    # project.monorepo_root
    mr = _deep_get(cfg, ("project", "monorepo_root"))
    if isinstance(mr, str):
        abs_path = (config_dir / mr).resolve() if not Path(mr).is_absolute() else Path(mr)
        cfg["project"]["monorepo_root"] = str(abs_path)

    # django.apps: Pfade pro App relativ machen
    apps = _deep_get(cfg, ("django", "apps"))
    if isinstance(apps, dict):
        new_apps = {}
        for app, p in apps.items():
            if isinstance(p, str):
                new_apps[app] = str((Path(cfg["project"]["monorepo_root"]) / p).resolve()) \
                    if not Path(p).is_absolute() else p
        cfg.setdefault("django", {})["apps"] = new_apps


def load_config(path: Union[str, Path]) -> dict:
    """
    Lädt die Projektkonfiguration, interpoliert Umgebungsvariablen,
    setzt Defaults, löst Pfade relativ zur Config-Datei und validiert.
    """
    cfg_path = Path(path).expanduser().resolve()
    cfg = _read_yaml(cfg_path)

    # Interpolation von ${ENV[:default]}
    cfg = _interpolate_env(cfg)

    # Defaults anwenden
    _apply_defaults(cfg, cfg_path.parent)

    # Pfade relativ zur Config-Datei auflösen
    _resolve_paths_relative_to_config(cfg, cfg_path.parent)

    # Validierung
    _validate_required(cfg)

    return cfg


# ---- kleine Hilfsfunktionen für Konsumenten ----

def get_project_root(cfg: Mapping[str, Any]) -> Path:
    root = _deep_get(cfg, ("project", "monorepo_root"))
    return Path(str(root)) if root else Path(".")


def get_app_path(cfg: Mapping[str, Any], app_name: str) -> Path:
    apps = _deep_get(cfg, ("django", "apps"), {})
    if not isinstance(apps, Mapping) or app_name not in apps:
        raise ConfigError(f"Unbekannte App '{app_name}'. Definiere sie unter django.apps in der Config.")
    return Path(str(apps[app_name]))


def pretty(cfg: Mapping[str, Any]) -> str:
    """Schöne JSON-Darstellung (z. B. für Debug-Ausgaben)."""
    return json.dumps(cfg, ensure_ascii=False, indent=2)
