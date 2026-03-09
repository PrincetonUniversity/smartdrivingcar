"""HTTP-triggered Azure Function that processes newsletter HTML into Jekyll markdown."""
import json
import logging

import azure.functions as func

from newsletter_processor import process

bp = func.Blueprint()


@bp.route(route="process-newsletter", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def process_newsletter(req: func.HttpRequest) -> func.HttpResponse:
    """Process newsletter HTML and return Jekyll-ready markdown."""
    logging.info("Processing newsletter request")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    body_html = body.get("body_html")
    if not body_html:
        return func.HttpResponse(
            json.dumps({"error": "Missing body_html field"}),
            status_code=400,
            mimetype="application/json",
        )

    subject = body.get("subject", "")
    received_date = body.get("received_date", "")
    known_slugs = body.get("known_slugs", [])

    try:
        result = process(body_html, subject, received_date, known_slugs)
    except Exception as e:
        logging.exception("Error processing newsletter")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json",
    )
