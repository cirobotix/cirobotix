# cirobotix

> Build software like a machine — not by chance.

![CI](https://github.com/cirobotix/cirobotix/actions/workflows/ci.yml/badge.svg)
![Docs](https://img.shields.io/badge/docs-online-blue)
![Python](https://img.shields.io/badge/python-3.9-blue)
![License](https://img.shields.io/badge/license-TBD-lightgrey)

---

## 🚀 What is cirobotix?

**cirobotix** is an **architecture-driven software production system**.

It does **not** generate code randomly.  
It produces **controlled, validated, and reproducible software artifacts**.

---

## ❌ The Problem

Modern development is fundamentally inconsistent:

- Quality depends on individuals  
- Architecture is documented, but not enforced  
- Reviews are subjective  
- AI tools generate fast but unreliable code  
- Documentation and code drift apart  

---

## ✅ The cirobotix Approach

cirobotix replaces guesswork with a deterministic pipeline:

```
Architecture → Rules → Generation → Validation → Artifact
```

Every output is:

- ✅ reproducible  
- ✅ testable  
- ✅ validated  
- ✅ compliant with defined standards  

---

## ⚔️ Not another AI Code Generator

| AI Code Tools | cirobotix |
|--------------|----------|
| probabilistic output | deterministic output |
| prompt-driven | architecture-driven |
| inconsistent results | reproducible artifacts |
| optional quality checks | enforced quality gates |
| docs are separate | docs are generated |

> cirobotix uses AI only as **assistive tooling**, not as the source of truth.

---

## ⚙️ Quality Pipeline

Every change must pass:

- 🧪 Unit Tests (`pytest`)
- 🧹 Linting & Formatting (`ruff`)
- 🔐 Security Analysis (`bandit`)
- 🧟 Dead Code Detection (`vulture`)
- 📚 Documentation Build (`mkdocs`)

No exceptions.

---

## 🏗️ Core Concepts

- **Blueprints**  
  Abstract, reusable component definitions  

- **Work Orders**  
  Concrete generation instructions  

- **Production Context**  
  Runtime pipeline state  

- **Executors**  
  Deterministic transformation units  

---

## 🔄 Development Workflow

```
feature/* → dev → main
```

- `feature/*` → isolated development  
- `dev` → integration  
- `main` → stable production  

### Automated Flow

- Push to `feature/*`  
  → CI runs  
  → PR to `dev` created automatically  

- Merge to `dev`  
  → CI runs  
  → PR to `main` created automatically  

- Merge to `main`  
  → Documentation is deployed  

---

## 📦 Project Structure

```
core/        # core engine
tests/       # validation
docs/        # documentation
.github/     # CI/CD workflows
```

---

## 📚 Documentation

👉 https://cirobotix.github.io/cirobotix/

---

## 🔮 Vision

cirobotix evolves into an **architecture compiler**:

```
Specification → Verified Implementation
```

Not faster coding.  
**Better systems.**

---

## 💬 Philosophy

cirobotix does not generate code.

It produces **controlled software artifacts**.

---

## 🛠️ Status

🚧 Early stage — actively evolving

---

## 🤝 Contributing

Currently optimized for internal development.  
Public contribution model coming soon.

---

## 📜 License

TBD
