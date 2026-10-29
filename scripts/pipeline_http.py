"""Bounded HTTPS client. Never follow redirects carrying bearer credentials."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class APIError(RuntimeError):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"API request failed (HTTP {status_code})")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


def request_json(
    url: str,
    *,
    host: str,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    method: str = "GET",
    expect_json: bool = True,
) -> Any:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != host
        or parsed.port not in (None, 443)
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError("Disallowed API destination")
    payload = json.dumps(data).encode() if data is not None else None
    request = Request(
        url,
        data=payload,
        headers={
            "User-Agent": "SmartDrivingCar-Publisher/1",
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method=method,
    )
    for attempt in range(4):
        try:
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                raw = response.read(10_000_001)
                if len(raw) > 10_000_000:
                    raise ValueError("API response exceeds size limit")
                return json.loads(raw) if raw and expect_json else {}
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 3:
                raise APIError(error.code) from None
            retry = error.headers.get("Retry-After", "")
            delay = min(int(retry), 60) if retry.isdigit() else 2**attempt
        except (URLError, TimeoutError):
            if attempt == 3:
                raise RuntimeError("API request failed (network timeout or connection)") from None
            delay = 2**attempt
        time.sleep(delay)
    raise RuntimeError("API retry limit reached")
