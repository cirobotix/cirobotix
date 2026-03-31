# CLI & Befehle

Aktuell wird cirobotix primär über `make`-Targets bedient.

## Verfügbare Hauptbefehle

- `make ai-draft TASK=...`
- `make promote REQUEST_ID=...`
- `make generate REQUEST_ID=...`

## Qualitätsbefehle

- `pytest`
- `ruff check .`
- `bandit -r . -c bandit.yml`
- `vulture core . --exclude tests/,.venv/,docs/,site/ --min-confidence 80`
- `mkdocs build --strict`

## Hinweise

- Nutze stabile, sprechende `REQUEST_ID`s.
- Halte `tasks/*.yaml` klein und fokussiert.
