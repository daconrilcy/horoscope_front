"""Fabriques de réponses HTTP pour les exports de l'API v1."""

from __future__ import annotations

import csv
import io
from typing import Any

from fastapi.responses import StreamingResponse


def generate_csv_response(
    rows: list[dict[str, Any]],
    fieldnames: list[str],
    filename: str,
    *,
    extra_headers: dict[str, str] | None = None,
) -> StreamingResponse:
    """Construit une réponse CSV téléchargeable pour les routeurs API v1."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    if extra_headers:
        headers.update(extra_headers)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )
