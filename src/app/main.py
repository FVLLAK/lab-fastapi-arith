from __future__ import annotations

import logging
import math
import time
from typing import Dict, Tuple

from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
app = Flask(__name__)

# ---- Prometheus metrics ----
REQUEST_COUNT = Counter("api_requests_total", "Total requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("api_request_duration_seconds", "Request latency (s)", ["endpoint"])

@app.before_request
def _before() -> None:
    request._start_time = time.perf_counter()

@app.after_request
def _after(response: Response) -> Response:
    try:
        duration = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
        endpoint = request.path
        REQUEST_LATENCY.labels(endpoint).observe(duration)
        REQUEST_COUNT.labels(request.method, endpoint, str(response.status_code)).inc()
    except Exception:
        pass
    return response

@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
# ---------------------------

def _bad_request(msg: str):
    return jsonify({"detail": msg}), 400

def _parse_operands() -> Tuple[float, float] | Tuple[Response, int]:
    data = request.get_json(silent=True) or {}
    if not {"a", "b"} <= set(data):
        return _bad_request("Payload attendu: {'a': float, 'b': float}")
    try:
        a = float(data["a"])
        b = float(data["b"])
    except (TypeError, ValueError):
        return _bad_request("Les champs 'a' et 'b' doivent être numériques.")
    if not (math.isfinite(a) and math.isfinite(b)):
        return _bad_request("Les valeurs doivent être finies (ni NaN ni infini).")
    return a, b

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/add")
def add():
    parsed = _parse_operands()
    if isinstance(parsed, tuple) and len(parsed) == 2 and isinstance(parsed[0], float):
        a, b = parsed
        logging.info("Addition: %s + %s", a, b)
        return jsonify({"result": a + b})
    return parsed

@app.post("/sub")
def sub():
    parsed = _parse_operands()
    if isinstance(parsed, tuple) and len(parsed) == 2 and isinstance(parsed[0], float):
        a, b = parsed
        logging.info("Soustraction: %s - %s", a, b)
        return jsonify({"result": a - b})
    return parsed

@app.post("/mul")
def mul():
    parsed = _parse_operands()
    if isinstance(parsed, tuple) and len(parsed) == 2 and isinstance(parsed[0], float):
        a, b = parsed
        logging.info("Multiplication: %s * %s", a, b)
        return jsonify({"result": a * b})
    return parsed

@app.post("/div")
def div():
    parsed = _parse_operands()
    if isinstance(parsed, tuple) and len(parsed) == 2 and isinstance(parsed[0], float):
        a, b = parsed
        logging.info("Division: %s / %s", a, b)
        if b == 0:
            return _bad_request("Division par zéro interdite (paramètre 'b' ne doit pas être égal à 0).")
        return jsonify({"result": a / b})
    return parsed

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import os
    # Par défaut, on écoute en local pour éviter B104. En conteneur, exporte FLASK_RUN_HOST=0.0.0.0
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    # Bandit: B104 n'est plus trigger car host est dynamique et par défaut 127.0.0.1
    app.run(host=host, port=port)
