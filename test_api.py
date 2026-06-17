"""
Smoke tests for VidCore API server.
Run with: python test_api.py
Requires api_server to be imported (starts in-process).
"""

import json
import threading
import time
from pathlib import Path

from fastapi.testclient import TestClient

from api_server import app, jobs
from core.paths import videos_dir
from core.paths import videos_dir

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["app"] == "VidCore API"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "vllm" in data


def test_videos():
    r = client.get("/videos")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_upload():
    r = client.post("/upload", files={"file": ("test.mp4", b"fake video data", "video/mp4")})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "test.mp4"
    # cleanup
    (videos_dir() / "test.mp4").unlink(missing_ok=True)


def test_analyze_missing():
    r = client.post("/analyze?video=/nonexistent.mp4")
    assert r.status_code == 404


def test_analyze_valid():
    # use the .gitkeep file (guaranteed to exist)
    gitkeep = str(videos_dir() / ".gitkeep")
    r = client.post(f"/analyze?video={gitkeep}&depth=scene-only")
    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    assert data["job_id"] in jobs
    jobs.pop(data["job_id"], None)


def test_list_jobs():
    jobs["test-123"] = {"id": "test-123", "video": "x.mp4", "status": "running"}
    r = client.get("/jobs")
    assert r.status_code == 200
    data = r.json()
    assert any(j["id"] == "test-123" for j in data)
    jobs.pop("test-123", None)


def test_status_missing():
    r = client.get("/status/nonexistent")
    assert r.status_code == 404


def test_context_missing():
    r = client.get("/context/nonexistent")
    assert r.status_code == 404


def test_key_events_missing():
    r = client.get("/key_events/nonexistent")
    assert r.status_code == 404


def test_reels_missing():
    r = client.get("/reels/nonexistent")
    assert r.status_code == 404


def test_report_missing():
    r = client.get("/report/nonexistent")
    assert r.status_code == 404


def test_csv_missing():
    r = client.get("/csv/nonexistent")
    assert r.status_code == 404


def test_delete_job():
    jobs["test-del"] = {"id": "test-del"}
    r = client.delete("/jobs/test-del")
    assert r.status_code == 200
    assert "test-del" not in jobs


def test_delete_missing():
    r = client.delete("/jobs/nonexistent")
    assert r.status_code == 404


def test_job_lifecycle():
    """Simulate a job through its lifecycle: create → status → data endpoints → delete."""
    video = str(videos_dir() / ".gitkeep")
    r = client.post(f"/analyze?video={video}&depth=scene-only")
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # check it appears in jobs list
    r = client.get("/jobs")
    jobs_list = r.json()
    assert any(j["id"] == job_id for j in jobs_list)

    # status returns 200
    r = client.get(f"/status/{job_id}")
    assert r.status_code == 200
    assert r.json()["id"] == job_id

    # data endpoints return 404 (no analysis ran, no WS connected)
    # but they should NOT 500 — they should handle gracefully
    for ep in ["/context", "/key_events", "/reels", "/report", "/csv"]:
        r = client.get(f"{ep}/{job_id}")
        assert r.status_code in (200, 404), f"{ep} returned {r.status_code}"

    # delete
    r = client.delete(f"/jobs/{job_id}")
    assert r.status_code == 200

    # gone
    r = client.get(f"/status/{job_id}")
    assert r.status_code == 404


if __name__ == "__main__":
    import sys
    passed = 0
    failed = 0
    for name in sorted(globals()):
        if name.startswith("test_"):
            fn = globals()[name]
            try:
                fn()
                print(f"  PASS  {name}")
                passed += 1
            except Exception as e:
                print(f"  FAIL  {name}: {e}")
                failed += 1

    print(f"\n{passed} passed, {failed} failed")

    # ── manual E2E API instructions ──
    print(f"""
{'='*60}
Manual API E2E test (requires vLLM + api_server running):

  # Terminal 1: start API
  python api_server.py

  # Terminal 2: pip install websocket-client, then:
  python manual_api_e2e.py
{'='*60}
""")
