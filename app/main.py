"""Simple web application template."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    """Return a basic HTTP response for the root endpoint."""
    return jsonify(service="template-devops-project", status="ok"), 200


@app.get("/health")
def health():
    """Return a simple health response for liveness/readiness probes."""
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
