from __future__ import annotations

from starlette.requests import Request

from app.core.request_id import resolve_request_id


def _build_request(*, header_request_id: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if header_request_id is not None:
        headers.append((b"x-request-id", header_request_id.encode("utf-8")))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }
    return Request(scope)


def test_resolve_request_id_strips_control_characters_from_header() -> None:
    request = _build_request(header_request_id="rid-good\r\ninjected")

    resolved = resolve_request_id(request)

    assert resolved == "rid-goodinjected"


def test_resolve_request_id_uses_sanitized_existing_state_value() -> None:
    request = _build_request()
    request.state.request_id = " keep-me\tok "

    resolved = resolve_request_id(request)

    assert resolved == "keep-meok"
    assert request.state.request_id == "keep-meok"


def test_resolve_request_id_generates_when_header_is_only_control_chars() -> None:
    request = _build_request(header_request_id="\r\n\t")

    resolved = resolve_request_id(request)

    assert len(resolved) == 32
    assert resolved.isalnum()
