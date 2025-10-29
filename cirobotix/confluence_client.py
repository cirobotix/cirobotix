# cirobotix/confluence_client.py
from __future__ import annotations
import os
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
import requests
from requests.adapters import HTTPAdapter, Retry

log = logging.getLogger(__name__)


class ConfluenceClient:
    def __init__(
            self,
            base_url: str,
            email_env: str = "CONFLUENCE_EMAIL",
            token_env: str = "CONFLUENCE_TOKEN",
            timeout_s: int = 20,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = os.getenv(email_env)
        self.token = os.getenv(token_env)
        if not self.email or not self.token:
            raise RuntimeError(
                f"Confluence credentials missing. Set {email_env} and {token_env}."
            )
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.auth = (self.email, self.token)
        self.timeout_s = timeout_s

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api{path}"
        r = self.session.get(url, params=params, timeout=self.timeout_s)
        if r.status_code == 429:
            # extra backoff in addition zu Retry
            retry_after = int(r.headers.get("Retry-After", "1"))
            time.sleep(min(retry_after, 5))
        r.raise_for_status()
        return r.json()

    def search_pages(
            self,
            space: str,
            cql: str,
            expand: str = "body.storage,version",
            limit: int = 50,
            max_pages: int = 200,
            debug: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Führt eine CQL-Suche aus und paginiert Ergebnisse.
        """
        results: List[Dict[str, Any]] = []
        start = 0
        if debug:
            log.warning(f"[Confluence] SPACE={space} CQL={cql}")
        while True:
            page = self._get(
                "/content/search",
                {
                    "cql": f"space = {space} AND ({cql})",
                    "expand": expand,
                    "limit": limit,
                    "start": start,
                },
            )
            values = page.get("results", [])
            results.extend(values)
            if debug:
                log.warning(
                    f"[Confluence] batch size={len(values)} "
                    f"total={len(results)} start={start}")
            if not values or len(values) < limit or len(results) >= max_pages:
                break
            start += limit
        return results

    # --- High-level Helper für unseren MVP ---

    def fetch_arc42_for_app(
            self,
            space: str,
            app_label: str,
            arc42_label: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Holt die (eine) arc42-Seite für eine App anhand von zwei Labels:
        z. B. labels = ["app:research", "arc42"].
        Liefert das erste Match (Storage HTML + Metadaten).
        """
        cql = f'type = "page" AND label = "{app_label}" AND label = "{arc42_label}"'
        pages = self.search_pages(space=space, cql=cql, limit=25, max_pages=25, debug=True)
        return pages[0] if pages else None

    def fetch_adrs_for_app(
            self,
            space: str,
            app_label: str,
            adr_label: str,
            max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Holt ADR-Seiten (Titel + Storage-Body) für die App. Begrenzt auf max_items.
        """
        cql = f'type = "page" AND label = "{app_label}" AND label = "{adr_label}"'
        pages = self.search_pages(space=space, cql=cql, limit=25,
                                  max_pages=max_items, debug=True)
        return pages[:max_items]


def extract_storage_html(page: Dict[str, Any]) -> str:
    """
    Gibt den Confluence-Storage-HTML-Body zurück (oder leere Zeichenkette).
    """
    return (
        page.get("body", {})
            .get("storage", {})
            .get("value", "")
    )


def page_title(page: Dict[str, Any]) -> str:
    return page.get("title", "")
