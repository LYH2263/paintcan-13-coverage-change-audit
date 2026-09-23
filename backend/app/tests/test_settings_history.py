import json
import pytest
from app import seed
from app.db import connect
from app.services.paint_service import PaintService
from app.repositories import settings as settings_repo

@pytest.fixture()
def db(monkeypatch, tmp_path):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    seed.init_db()
    yield

def test_change_appends_history(db):
    with PaintService() as s:
        res = s.save_settings({"coverage": 10})
        assert [c["field"] for c in res["changed"]] == ["coverage"]
        assert res["changed"][0]["old_value"] == "8"
        assert res["changed"][0]["new_value"] == "10"
        assert s.settings()["coverage"] == "10"
        hist = s.settings_history()
        assert len(hist) == 1
        assert hist[0]["field"] == "coverage"

def test_same_value_appends_nothing(db):
    with PaintService() as s:
        s.save_settings({"coverage": 10})
        res = s.save_settings({"coverage": 10, "coats": 2})
        assert res["changed"] == []
        assert len(s.settings_history()) == 1

def test_numeric_equivalence_no_duplicate(db):
    with PaintService() as s:
        # 8.0 与库中 "8" 数值相同，不得追加
        res = s.save_settings({"coverage": 8.0})
        assert res["changed"] == []
        assert s.settings_history() == []

def test_invalid_value_rolls_back_setting_and_history(db):
    with PaintService() as s:
        s.save_settings({"coverage": 10})
        with pytest.raises(ValueError):
            # coverage=7 先写入事务，coats=0 非法 -> 整体回滚
            settings_repo.save(s._c, {"coverage": 7, "coats": 0})
        assert s.settings()["coverage"] == "10"
        assert len(s.settings_history()) == 1

def test_old_run_pinned_after_default_changes(db):
    with PaintService() as s:
        old = s.estimate(1, persist=True)
        assert old["liters"] == 11.6 and old["coverage"] == 8.0 and old["coats"] == 2
        s.save_settings({"coverage": 10, "coats": 3})
        # 改默认后重开旧条：升数与钉选涂布率/遍数仍为写入时数值
        old_run = next(r for r in s.history() if r["id"] == old["run_id"])
        pin = json.loads(old_run["input_json"])
        result = json.loads(old_run["result_json"])
        assert pin["coverage"] == 8.0 and pin["coats"] == 2
        assert result["liters"] == 11.6 and result["coverage"] == 8.0 and result["coats"] == 2
        # 房间新测才采用新默认
        new = s.estimate(1, persist=True)
        assert new["coverage"] == 10.0 and new["coats"] == 3
        assert new["liters"] == round(46.41 * 3 / 10, 2)
