"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging

from fastapi import APIRouter

router = APIRouter(prefix="/email", tags=["email"])
logger = logging.getLogger(__name__)


def _get_confirmation_html(success: bool, message: str) -> str:
    title = "Désabonnement réussi" if success else "Erreur de désabonnement"
    icon = "✨" if success else "⚠️"
    extra_msg = (
        "<p>Vous continuerez à recevoir les emails essentiels liés à votre compte.</p>"
        if success
        else ""
    )
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f4edf6;
                margin: 0;
            }}
            .card {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
            }}
            h1 {{ color: #111938; }}
            p {{ color: #666; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{title} {icon}</h1>
            <p>{message}</p>
            {extra_msg}
        </div>
    </body>
    </html>
    """
