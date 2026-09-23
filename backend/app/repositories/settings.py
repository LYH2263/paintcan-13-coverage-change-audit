import sqlite3
from datetime import datetime, timezone

FIELDS = ("coverage", "coats")

def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}
def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))

def _canonical(key, value):
    if key == "coverage":
        v = float(value)
        if v <= 0:
            raise ValueError(f"{key} 必须为正数")
        raw = str(int(v)) if v.is_integer() else str(v)
    else:
        v = int(value)
        if v <= 0:
            raise ValueError(f"{key} 必须为正数")
        raw = str(v)
    return v, raw

def list_history(conn, limit=100):
    return [dict(r) for r in conn.execute(
        "SELECT id, field, old_value, new_value, changed_at FROM settings_history ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall()]

def save(conn, updates):
    """单事务保存默认值：仅当新值与库中当前值（按数值比较）不同时才更新并追加履历。
    任一字段校验失败则整体回滚，设置与履历保持一致。"""
    current = get_map(conn)
    changed = []
    with conn:
        for key in FIELDS:
            if updates.get(key) is None:
                continue
            new_val, new_raw = _canonical(key, updates[key])
            old_raw = current.get(key)
            if old_raw is not None:
                old_val, _ = _canonical(key, old_raw)
                if old_val == new_val:
                    continue
            conn.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, new_raw))
            now = datetime.now(timezone.utc).isoformat()
            cur = conn.execute(
                "INSERT INTO settings_history(field,old_value,new_value,changed_at) VALUES(?,?,?,?)",
                (key, old_raw if old_raw is not None else "", new_raw, now))
            changed.append({"id": int(cur.lastrowid), "field": key,
                            "old_value": old_raw, "new_value": new_raw, "changed_at": now})
    return {"settings": get_map(conn), "changed": changed}
