from __future__ import annotations

import argparse
import json
import logging
import traceback

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app


def _setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug direct API call /v1/natal/interpretation.")
    parser.add_argument("--user-id", type=int, default=4)
    parser.add_argument("--role", type=str, default="user")
    parser.add_argument("--request-id", type=str, default="debug-api-natal-001")
    parser.add_argument("--persona-id", type=str, default="dec97b57-4705-4166-8aea-8ea1567d24e9")
    parser.add_argument("--locale", type=str, default="fr-FR")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    _setup_logging(args.debug)
    logger = logging.getLogger("debug_api_natal_call")

    token = create_access_token(subject=str(args.user_id), role=args.role)
    headers = {
        "Authorization": f"Bearer {token}",
        "x-request-id": args.request_id,
    }
    payload = {
        "use_case_level": "complete",
        "persona_id": args.persona_id,
        "locale": args.locale,
        "force_refresh": args.force_refresh,
    }

    client = TestClient(app, raise_server_exceptions=True)
    try:
        resp = client.post("/v1/natal/interpretation", headers=headers, json=payload)
        logger.info("status=%s", resp.status_code)
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception as exc:
        logger.error("API call crashed: %s", exc)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

