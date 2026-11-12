import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, request, abort
from config import Config
from utils import parse_log_file, filter_logs_by_datetime, filter_logs_by_status

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the main dashboard."""
    return render_template("index.html")


@app.route("/api/logs", methods=["GET"])
def api_logs():
    """
    Return parsed logs as JSON.
    Optional query parameters:
        - start: ISO‑8601 datetime string
        - end:   ISO‑8601 datetime string
        - status: HTTP status code (int)
    """
    try:
        raw_logs = parse_log_file(app.config["LOG_FILE"])
    except FileNotFoundError as exc:
        logger.error("Log file not found: %s", exc)
        abort(404, description="Log file not found.")
    except Exception as exc:
        logger.exception("Failed to parse log file.")
        abort(500, description=str(exc))

    # Apply filters if present
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    status_str = request.args.get("status")

    filtered = raw_logs

    if start_str or end_str:
        try:
            start_dt = datetime.fromisoformat(start_str) if start_str else None
            end_dt = datetime.fromisoformat(end_str) if end_str else None
            filtered = filter_logs_by_datetime(filtered, start_dt, end_dt)
        except ValueError as exc:
            logger.warning("Invalid datetime filter: %s", exc)
            abort(400, description="Invalid datetime format. Use ISO‑8601.")

    if status_str:
        try:
            status_code = int(status_str)
            filtered = filter_logs_by_status(filtered, status_code)
        except ValueError:
            abort(400, description="Status must be an integer.")

    return jsonify(filtered)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting Log Analyzer Visualizer")
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])