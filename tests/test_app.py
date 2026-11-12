import json
import os
import tempfile
import pytest
from app import app as flask_app

# ---------------------------------------------------------------------------
# Helper to create a temporary log file with known content
# ---------------------------------------------------------------------------

LOG_CONTENT = """127.0.0.1 - frank [10/Oct/2023:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326
127.0.0.1 - john [10/Oct/2023:14:02:01 -0700] "POST /submit HTTP/1.1" 404 721
"""

@pytest.fixture
def client():
    # Create a temporary log file
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(LOG_CONTENT)

    # Override config for the test
    flask_app.config["TESTING"] = True
    flask_app.config["LOG_FILE"] = path

    with flask_app.test_client() as client:
        yield client

    os.remove(path)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Log Analyzer & Visualizer" in resp.data

def test_api_logs_all(client):
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["status"] == 200
    assert data[1]["status"] == 404

def test_api_logs_filter_status(client):
    resp = client.get("/api/logs?status=404")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]["status"] == 404

def test_api_logs_invalid_datetime(client):
    resp = client.get("/api/logs?start=invalid")
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert "Invalid datetime format" in data["error"]