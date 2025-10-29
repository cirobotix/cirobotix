# cirobotix/jira_client.py
from __future__ import annotations

import os
import requests
from typing import List, Dict, Any, Optional
from rich import print


class JiraClient:
    """
    Leichter Wrapper für Jira Cloud REST API (v3).
    Unterstützt Basic Auth via Umgebungsvariablen (E-Mail + Token).

    Erwartete Endpunkte:
      - GET /rest/api/3/project/{key}
      - GET /rest/api/3/field
      - GET /rest/api/3/search?jql=...
    """

    def __init__(
        self,
        base_url: str,
        email_env: str = "JIRA_EMAIL",
        token_env: str = "JIRA_TOKEN",
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = os.getenv(email_env)
        self.token = os.getenv(token_env)
        self.timeout = timeout

        if not self.email or not self.token:
            raise RuntimeError(
                f"Jira credentials not found in env vars {email_env}/{token_env}"
            )

        self._session = requests.Session()
        self._session.auth = (self.email, self.token)
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "cirobotix-jira-client/1.0",
            }
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        if path.startswith("rest/api"):
            return f"{self.base_url}/{path}"
        return f"{self.base_url}/rest/api/3/{path}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = self._url(path)
        resp = self._session.get(url, params=params or {}, timeout=self.timeout)
        if resp.status_code >= 400:
            raise RuntimeError(
                f"Jira GET {url} failed: {resp.status_code} {resp.text[:200]}"
            )
        return resp.json()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def get_project(self, key: str) -> Dict[str, Any]:
        """Liest Projektdetails (inkl. simplified-Flag)."""
        return self._get(f"project/{key}")

    def get_fields(self) -> List[Dict[str, Any]]:
        """Liest alle Felddefinitionen."""
        return self._get("field")

    def search(
        self,
        jql: str,
        startAt: int = 0,
        maxResults: int = 50,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Führt eine Jira-JQL-Suche aus (inkl. Pagination).
        Ab Jira Cloud API-Änderung 2024 muss der neue Pfad /rest/api/3/search/jql genutzt werden.
        """
        params: Dict[str, Any] = {
            "jql": jql,
            "startAt": startAt,
            "maxResults": maxResults,
        }
        if fields:
            params["fields"] = ",".join(fields)

        try:
            # neue API-Route
            return self._get("search/jql", params=params)
        except RuntimeError as e:
            msg = str(e)
            # Rückfall für ältere Jira-Versionen
            if "410" in msg or "removed" in msg or "migrate" in msg:
                print("[yellow]⚠️ Jira API notice: using legacy /search fallback[/]")
                return self._get("search", params=params)
            raise

    # Convenience Wrapper für cirobotix CLI
    def search_all(
        self,
        jql: str,
        page_size: int = 100,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Liest alle Issues für ein JQL mit automatischer Pagination."""
        start, total, results = 0, 1, []
        while start < total:
            data = self.search(jql, startAt=start, maxResults=page_size, fields=fields)
            issues = data.get("issues", [])
            results.extend(issues)
            total = data.get("total", 0)
            if not issues:
                break
            start += len(issues)
        return results

    # Simple diagnostic
    def ping(self) -> bool:
        """Einfacher Test: prüft, ob Auth funktioniert."""
        try:
            self._get("myself")
            print("[green]✅ Jira connection OK[/]")
            return True
        except Exception as e:
            print(f"[red]❌ Jira connection failed:[/] {e}")
            return False
