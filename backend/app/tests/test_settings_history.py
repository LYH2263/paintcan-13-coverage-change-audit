import json
import pytest
from fastapi.testclient import TestClient

from app import db, seed
from app.main import app
from app.repositories import settings as settings_repo
from app.services.paint_service import PaintService

@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return db

def test_noop_save_appends_nothing(tmp_db):
    with PaintService() as s:
        out = s.update_settings({"coverage": 8.0})
    assert out["changed"] == []
    with PaintService() as s:
        assert s.settings_history() == []
        assert s.settings()["coverage"] == "8"  # canonicalized, not "8.0"

def test_changed_value_appends_one_row(tmp_db):
    with PaintService() as s:
        out = s.update_settings({"coverage": 10})
    assert [(r["field"], r["old_value"], r["new_value"]) for r in out["changed"]] == [("coverage", "8", "10")]
    with PaintService() as s:
        hist = s.settings_history()
        assert len(hist) == 1
        assert hist[0]["field"] == "coverage"
        assert hist[0]["old_value"] == "8"
        assert hist[0]["new_value"] == "10"
        assert hist[0]["changed_at"]
        cov, coats = settings_repo.coverage_coats(db.connect())
    assert (cov, coats) == (10.0, 2)

def test_mixed_request_only_logs_changed_field(tmp_db):
    with PaintService() as s:
        out = s.update_settings({"coverage": 10, "coats": 2})
    assert [r["field"] for r in out["changed"]] == ["coverage"]
    with PaintService() as s:
        assert len(s.settings_history()) == 1

def test_invalid_input_changes_nothing(tmp_db):
    for bad in ({"coverage": 0}, {"coverage": -1}, {"coats": 0}, {"coats": 2.5}):
        with PaintService() as s:
            with pytest.raises(ValueError):
                s.update_settings(bad)
    with PaintService() as s:
        assert s.settings() == {"coverage": "8", "coats": "2"}
        assert s.settings_history() == []

def test_history_is_reverse_chronological(tmp_db):
    with PaintService() as s:
        s.update_settings({"coverage": 9})
        s.update_settings({"coats": 3})
        hist = s.settings_history()
    assert [r["field"] for r in hist] == ["coats", "coverage"]

def test_saved_run_is_immutable_after_default_change(tmp_db):
    with PaintService() as s:
        before = s.estimate(1, True)
    assert before["coverage"] == 8.0 and before["coats"] == 2
    pinned_liters = before["liters"]
    with PaintService() as s:
        s.update_settings({"coverage": 99, "coats": 7})
        rows = s.history(10)
    old = next(r for r in rows if r["id"] == before["run_id"])
    result = json.loads(old["result_json"])
    inp = json.loads(old["input_json"])
    assert result["liters"] == pinned_liters
    assert result["coverage"] == 8.0
    assert result["coats"] == 2
    assert inp["coverage"] == 8.0 and inp["coats"] == 2
    # a new measurement uses the new defaults
    with PaintService() as s:
        after = s.estimate(1, True)
    assert after["coverage"] == 99.0 and after["coats"] == 7
    assert after["liters"] != pinned_liters

def test_api_post_settings_and_history(tmp_db):
    client = TestClient(app)
    r = client.post("/api/settings", json={"coverage": 8})
    assert r.status_code == 200
    assert r.json()["changed"] == []
    r = client.post("/api/settings", json={"coverage": 10, "coats": 2})
    assert r.status_code == 200
    assert [c["field"] for c in r.json()["changed"]] == ["coverage"]
    items = client.get("/api/settings/history").json()["items"]
    assert len(items) == 1 and items[0]["new_value"] == "10"
    bad = client.post("/api/settings", json={"coverage": 0})
    assert bad.status_code == 400
    assert len(client.get("/api/settings/history").json()["items"]) == 1
