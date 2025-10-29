# 🧠 Cirobotix

> **Cirobotix** is an intelligent automation framework for structured software development.  
> It connects **Confluence** (architecture documentation) and **Jira** (project planning)  
> to automatically generate **LLM-ready prompts** for code and test generation directly from the command line.

---

## 🚀 Current Status (October 2025)

Cirobotix currently **generates AI prompts** from your **Confluence arc42 documentation** and **Jira project tickets**.  
The generated prompts serve as direct input for code-generation models (e.g. GPT, Codex).

Implemented features:

| Category | Implemented Component | Description |
|-----------|----------------------|--------------|
| 🧩 Core | **CLI (`cirobotix`)** | Command-line interface for fetching context and generating prompts |
| 📄 Config | **YAML Project Config Parser** | Reads configuration (`*.project.yaml`) including Confluence, Jira, and Tech Stack settings |
| 📘 Confluence | **ConfluenceClient** | Fetches and parses architecture pages (arc42 format) and ADR pages |
| 🧱 Parser | **arc42 Extractor** | Extracts relevant sections (Goals, Constraints, Context, Solution Strategy, etc.) |
| 🧠 Jira | **JiraClient** | Queries Jira via REST API for Epics and related issues in “READY FOR GENERATE” state |
| 🧩 Jira Integration | **Jira Ready Selector** | Detects all Epics with at least one child ticket ready for generation |
| 🧬 Normalization | **ADF → Plaintext Converter** | Converts Atlassian Document Format to plain text for AI prompts |
| 🪄 Generator | **Prompt Builder** | Assembles context (arc42 + ADR + Jira issue) into a single structured AI prompt |
| ⚙️ Utility | **Tech Stack Profiles** | Configurable stack profiles (e.g. `django`, `java-selenium`, `generic`) control which files are targeted |
| 📦 Output | **JSON Context Export** | Stores merged Confluence + Jira data for reproducible AI workflows |

---

## 🧱 Project Setup Overview

### 1️⃣ Confluence (Architecture)

Each project has:
- One **arc42 page** (documenting your software architecture)
- One **ADR section** (Architecture Decision Records)

**Example structure:**

| Page | Type | Label |
|-------|------|--------|
| `/Architecture Overview` | arc42 | `arc42` |
| `/ADRs` | ADRs (ADR-01…ADR-07) | `adr` |

Required labels are configured under:

```yaml
confluence:
  labels:
    arc42: "arc42"
    adr: "adr"
    app_prefix: "app_"
```

Cirobotix will fetch all pages in the specified Confluence space with those labels.

---

### 2️⃣ Jira (Project Planning)

Each **Epic** represents a feature or module.  
Each **Story / Ticket** under that Epic describes a concrete implementation step.

Example workflow:
```
EPIC: Dataset Registry (CSV Import & Cleaning)
  ├── SMP-15: Create OHLCData model
  ├── SMP-16: Implement import endpoint
  └── SMP-17: Add admin registration
```

Tickets must have:
- `status = READY FOR GENERATE`
- acceptance criteria defined (optional but recommended)

Configuration in YAML:

```yaml
jira:
  base_url: "https://example.atlassian.net"
  project_key: "SMP"
  ready_status: "READY FOR GENERATE"
```

---

## 🧩 CLI Usage

### Generate a **context payload** and prompt from Confluence + Jira

```bash
cirobotix --app research --mode implement --tickets SMP-15
```

### Command reference

| Command | Description |
|----------|--------------|
| `cirobotix` | Main entry point; runs with default options |
| `cirobotix conf-fetch` | Explicit fetch + generation of context and prompts |
| `--project-config, -c` | Path to YAML configuration (default: `docs/cirobotix.project.yaml`) |
| `--app, -a` | Application name (e.g. `research`, `frontend`, `qa-suite`) |
| `--mode` | `plan` → create planning prompt; `implement` → create code prompt |
| `--tickets` | Comma-separated ticket keys (e.g. `SMP-15,SMP-16` or `*` for all) |
| `--stack` | Override tech stack profile (`django`, `java-selenium`, `generic`) |
| `--html-mode` | Confluence parsing mode (`markdown`, `text`, `raw`) |
| `--scope` | Generation scope (`ticket-only`, `epic`, `project`) |
| `--allow` | Additional allowed file paths for generation |
| `--base-setup` | Allow minimal project bootstrap if required |
| `--debug` | Print parsed arc42 section headings |
| `--include-jira/--no-include-jira` | Enable or skip Jira data enrichment |

---

### Example Workflow

```bash
# 1. Prepare your Confluence and Jira setup
# 2. Configure docs/cirobotix.project.yaml (or use sample_config.yaml)
# 3. Run the command
cirobotix --app research --mode implement --tickets SMP-15

# 4. Check generated context
cat cirobotix/context/_conf_sample.json

# 5. Use the printed prompt directly in GPT / code-generation pipeline
```

---

## 🧠 Example Output

```json
{
  "meta": {
    "app": "research",
    "generated_at": "2025-10-29T15:40:41Z"
  },
  "jira": {
    "project_key": "SMP",
    "candidates": [
      {"key": "SMP-15", "summary": "Create OHLCData model", "..." : "..."}
    ]
  },
  "arc42": {
    "goals": "...",
    "solution_strategy": "...",
    "constraints": "..."
  },
  "adrs": [
    {"title": "ADR-01 Template Method", "storage": "..."}
  ]
}
```

---

## 🧩 Tech Stack Configuration

Cirobotix supports **multiple technology stacks** via configuration.

```yaml
tech_stack:
  name: "java-selenium"
  languages:
    - name: "Java"
      version: "21"
  frameworks:
    - name: "Selenium"
      role: "UI testing"
```

---

## 🧪 Development

```bash
# Local installation
pip install -e .

# Run the CLI
cirobotix --help

# Use sample config
cirobotix --project-config docs/sample_config.yaml --app research --mode plan
```

---

## 📚 Roadmap

| Phase | Goal | Status |
|--------|------|---------|
| Phase 1 | CLI tool for prompt generation (Confluence + Jira) | ✅ Done |
| Phase 2 | Integration with GitLab (commit, MR, pipeline trigger) | ⏳ Planned |
| Phase 3 | Automated test generation & evaluation | 🔜 Planned |
| Phase 4 | Self-updating pipelines (Codex feedback loop) | 🔜 Planned |

---

## 🧩 License

MIT AND CEL-1.0
© 2025 Cirobotix Contributors
