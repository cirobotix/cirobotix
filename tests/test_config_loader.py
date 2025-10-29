# tests/test_config_loader.py
import os
import tempfile
import textwrap
import json
from pathlib import Path
import pytest

from cirobotix.config_loader import (
    load_config,
    get_project_root,
    get_app_path,
    pretty,
    ConfigError,
)

# ---------- Fixtures ----------

@pytest.fixture()
def sample_yaml(tmp_path: Path):
    """Erzeugt eine temporäre Projektkonfiguration."""
    yaml_text = textwrap.dedent(
        """
        project:
          name: "TestProject"
          monorepo_root: "."

        confluence:
          base_url: "https://${CONF_HOST:example.atlassian.net}/wiki"
          space: "ARCH"
          labels:
            arc42: "arc42"
            adr: "adr"
            app_prefix: "app:"
          arc42:
            heading_levels: [2, 3]
            max_chars_per_section: 5000
          adr:
            max_items: 3
            max_chars: 1500

        django:
          apps:
            research: "apps/research"
        """
    )
    path = tmp_path / "cirobotix.project.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    return path


# ---------- Tests ----------

def test_load_config_with_env_interpolation(monkeypatch, sample_yaml):
    """prüft, dass ENV Variablen ersetzt und Defaults ergänzt werden."""
    monkeypatch.setenv("CONF_HOST", "demo.atlassian.net")

    cfg = load_config(sample_yaml)

    # 1. Interpolation funktioniert
    assert "demo.atlassian.net" in cfg["confluence"]["base_url"]

    # 2. Defaults sind vorhanden
    assert "solution_strategy" in cfg["confluence"]["arc42"]["section_map"]

    # 3. Kontextbudget ergänzt
    assert cfg["context_budget"]["max_chars_total"] > 0

    # 4. Pfade relativ aufgelöst
    root = get_project_root(cfg)
    app_path = get_app_path(cfg, "research")
    assert app_path.is_absolute()
    assert str(root) in str(app_path)

    # 5. pretty() gibt valides JSON
    pretty_json = pretty(cfg)
    parsed = json.loads(pretty_json)
    assert "confluence" in parsed


def test_missing_confluence_raises(tmp_path):
    """Fehlerhafte Config ohne 'confluence' löst ConfigError aus."""
    invalid_yaml = tmp_path / "broken.yaml"
    invalid_yaml.write_text("foo: bar", encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(invalid_yaml)


def test_unknown_app_raises(sample_yaml):
    cfg = load_config(sample_yaml)
    with pytest.raises(ConfigError):
        get_app_path(cfg, "unknown")


def test_path_resolution_relative(tmp_path):
    """prüft, dass relative Pfade korrekt zu Absolutpfaden werden."""
    yaml_text = textwrap.dedent(
        """
        project:
          name: "RelProject"
          monorepo_root: "./monorepo"

        confluence:
          base_url: "https://example/wiki"
          space: "ARCH"
          labels:
            arc42: "arc42"
            adr: "adr"
            app_prefix: "app:"
        """
    )
    path = tmp_path / "conf.yaml"
    path.write_text(yaml_text, encoding="utf-8")

    cfg = load_config(path)
    root = get_project_root(cfg)
    assert root.is_absolute()
    assert "monorepo" in str(root)
