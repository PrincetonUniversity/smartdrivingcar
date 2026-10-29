"""Function-key protected adapter for existing Outlook connector batches."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import azure.functions as func

library = Path(__file__).resolve().parent / "lib"
if not library.is_dir():
    library = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(library))

from connector_batch import prepare_batch, settings_from_env  # noqa: E402

# Fail at worker startup if the publishing identity policy is not configured.
SETTINGS = settings_from_env()
connector_bp = func.Blueprint()


@connector_bp.route(
    route="prepare-connector-batch", methods=["POST"], auth_level=func.AuthLevel.FUNCTION
)
def prepare_connector_batch(req: func.HttpRequest) -> func.HttpResponse:
    if len(req.get_body()) > 8_000_000:
        return func.HttpResponse(
            '{"error":"request_too_large"}', status_code=413, mimetype="application/json"
        )
    try:
        body = req.get_json()
        if not isinstance(body, dict):
            raise ValueError("Expected object")
        limit = body.get("message_limit", 100)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ValueError("Invalid message limit")
        mode = body.get("mode")
        if not isinstance(mode, str):
            raise ValueError("Invalid mode")
        result = prepare_batch(
            body.get("messages"),
            mode,
            body.get("correlation_id", ""),
            {**SETTINGS, "limit": limit},
        )
    except (ValueError, TypeError, KeyError, AttributeError):
        logging.warning("Connector batch rejected: invalid input or policy validation")
        return func.HttpResponse(
            '{"error":"invalid_connector_batch"}', status_code=400, mimetype="application/json"
        )
    except Exception:
        logging.error("Connector batch failed: upstream inventory unavailable")
        return func.HttpResponse(
            '{"error":"connector_upstream_unavailable"}',
            status_code=503,
            mimetype="application/json",
        )
    logging.info(
        "Connector batch accepted; scanned=%d accepted=%d remaining=%d",
        result["scanned"],
        result["accepted"],
        result["remaining"],
    )
    return func.HttpResponse(json.dumps(result), status_code=200, mimetype="application/json")
