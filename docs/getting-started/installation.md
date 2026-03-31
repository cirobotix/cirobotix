# Installation

## Voraussetzungen

- Python 3.9+
- `pip`

## Variante 1: Installation direkt aus GitHub

```bash
pip install "git+https://github.com/cirobotix/cirobotix.git"
```

## Variante 2: Lokale Entwicklung

```bash
git clone https://github.com/cirobotix/cirobotix.git
cd cirobotix
pip install -e .
```

## Verifikation

```bash
cirobotix command=init path=. dry_run=true
```
