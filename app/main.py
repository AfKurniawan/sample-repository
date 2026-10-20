import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS


app = Flask(__name__)
# INTENTIONAL: permissive CORS is part of the security-analysis fixture.
CORS(app, resources={r"/*": {"origins": "*"}})

# INTENTIONAL: dummy-only value used to test secret detection.
INTERNAL_API_KEY = "sample-only-not-a-real-secret-123456"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "sample.db"

RUNTIME_EVENTS = [
    {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "message": "sample service started in local Docker mode",
        "source": "sample-service",
    },
    {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "WARN",
        "message": "debug mode is enabled for the security fixture",
        "source": "sample-service",
    },
]


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, status TEXT)"
    )
    if connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0:
        connection.executemany(
            "INSERT INTO items (name, status) VALUES (?, ?)",
            [("sample deployment", "attention"), ("sample worker", "healthy")],
        )
        connection.commit()
    return connection


@app.get("/healthz")
def healthz():
    if os.getenv("FAIL_HEALTHCHECK", "false").lower() == "true":
        return jsonify({"status": "unhealthy", "reason": "intentional fixture failure"}), 503
    return jsonify({"status": "ok", "service": "looks-sample-vulnerable"})


@app.get("/api/items")
def search_items():
    query = request.args.get("query", "")
    # INTENTIONAL: SQL injection fixture. Use parameterized SQL in real code.
    sql = f"SELECT id, name, status FROM items WHERE name LIKE '%{query}%';"
    with database() as connection:
        rows = connection.execute(sql).fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/files/<path:filename>")
def download_file(filename: str):
    # INTENTIONAL: path traversal fixture. Resolve and constrain paths in real code.
    return send_file(DATA_DIR / filename)


@app.get("/tools/echo")
def shell_echo():
    value = request.args.get("value", "sample")
    # INTENTIONAL: shell injection fixture. Never interpolate request data in a shell.
    result = subprocess.run(
        f"printf '%s' '{value}'",
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    return jsonify({"output": result.stdout, "returncode": result.returncode})


@app.post("/upload")
def upload():
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify({"error": "file is required"}), 400
    # INTENTIONAL: no size, extension, content, or storage policy validation.
    destination = DATA_DIR / (uploaded.filename or "unnamed-upload")
    uploaded.save(destination)
    return jsonify({"saved_as": str(destination)})


@app.get("/admin/config")
def admin_config():
    # INTENTIONAL: admin endpoint has no authentication or authorization.
    return jsonify({"internal_api_key": INTERNAL_API_KEY, "debug": app.debug})


@app.get("/unstable")
def unstable():
    if os.getenv("FAIL_RUNTIME", "false").lower() == "true":
        RUNTIME_EVENTS.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "ERROR",
                "message": "intentional sample runtime failure",
                "source": "sample-service",
            }
        )
        raise RuntimeError("intentional sample runtime failure")
    return jsonify({"status": "stable"})


@app.get("/logs")
def logs():
    return jsonify({"events": RUNTIME_EVENTS[-100:]})


@app.errorhandler(Exception)
def handle_error(error: Exception):
    # INTENTIONAL: debug-style internal error details leak to clients.
    return jsonify({"error": str(error), "type": type(error).__name__}), 500


if __name__ == "__main__":
    # INTENTIONAL: debug and all-interface binding represent deployment findings.
    app.run(host="0.0.0.0", port=8080, debug=True)
