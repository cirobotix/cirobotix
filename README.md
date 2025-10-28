# Cirobotix 

> **Cirobotix** is an open-source AI automation framework for Continuous Integration.  
> It connects **Jira**, **Confluence**, and **GitLab** to automatically generate, review, and deploy code through structured pipelines.

---

### Core Idea
Cirobotix turns your CI/CD pipeline into an intelligent production line.  
It parses project configurations, fetches Jira issues, reads architectural context from Confluence, and generates production-ready code.

### Components
- **Config Parser:** Reads YAML project manifests.
- **Jira Client:** Fetches and normalizes user stories.
- **Confluence Client:** Extracts architecture context (arc42 / ADRs).
- **Generator:** Uses AI models to produce code artifacts.
- **GitLab Client:** Commits, opens merge requests, updates issue states.

---

### Quick Start
```bash
git clone https://github.com/cirobotix/cirobotix.git
cd cirobotix
pip install -e .
cirobotix check --project-config docs/sample_config.yaml
