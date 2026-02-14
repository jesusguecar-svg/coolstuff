"""HTTP session with automatic retries, exponential backoff, and rate-limit
handling.

Every outbound HTTP call in the bot should go through ``get_session()`` so that
429 / 5xx / timeout retries are handled uniformly.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 15  # seconds
_MAX_RETRIES = 4
_BACKOFF_FACTOR = 1.0  # 1s, 2s, 4s, 8s


def _build_retry() -> Retry:
    return Retry(
        total=_MAX_RETRIES,
        backoff_factor=_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
        raise_on_status=False,
    )


def get_session(timeout: int = _DEFAULT_TIMEOUT) -> requests.Session:
    """Return a ``requests.Session`` wired with retry/backoff adapter."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_build_retry())
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.timeout = timeout  # type: ignore[attr-defined]
    return session


class ApiClient:
    """Lightweight wrapper that adds base URL, default headers, logging, and
    rate-limit awareness to a ``requests.Session``.
    """

    def __init__(self, base_url: str, timeout: int = _DEFAULT_TIMEOUT, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = get_session(timeout)
        if headers:
            self.session.headers.update(headers)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: dict[str, Any] | None = None, **kwargs: Any) -> requests.Response:
        url = self._url(path)
        logger.debug("GET %s params=%s", url, params)
        resp = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
        self._check_rate_limit(resp)
        return resp

    def post(self, path: str, json_data: dict[str, Any] | None = None, **kwargs: Any) -> requests.Response:
        url = self._url(path)
        logger.debug("POST %s", url)
        resp = self.session.post(url, json=json_data, timeout=self.timeout, **kwargs)
        self._check_rate_limit(resp)
        return resp

    def delete(self, path: str, json_data: dict[str, Any] | None = None, **kwargs: Any) -> requests.Response:
        url = self._url(path)
        logger.debug("DELETE %s", url)
        resp = self.session.delete(url, json=json_data, timeout=self.timeout, **kwargs)
        self._check_rate_limit(resp)
        return resp

    def _check_rate_limit(self, resp: requests.Response) -> None:
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "5"))
            logger.warning("Rate limited (429). Sleeping %ds before caller retries.", retry_after)
            time.sleep(retry_after)
