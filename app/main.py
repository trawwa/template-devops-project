"""Simple web application template."""

import logging
import sys
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


@app.before_request
def log_request():
    app.logger.info(
        "request=%s path=%s remote=%s",
        request.method,
        request.path,
        request.remote_addr,
    )


@app.get("/")
def index():
    """Return a basic HTTP response for the root endpoint."""
    return jsonify(service="template-devops-project", status="ok"), 200


@app.get("/health")
def health():
    """Return a simple health response for liveness/readiness probes."""
    return jsonify(status="ok"), 200


@app.get("/load")
def load():
    """Generate CPU load while the request is active."""
    duration_seconds = 3
    start = time.time()
    result = 0
    while time.time() - start < duration_seconds:
        result += 1  # CPU-bound work
    elapsed = time.time() - start
    return (
        jsonify(
            status="ok",
            load_duration=round(elapsed, 3),
            iterations=result,
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
