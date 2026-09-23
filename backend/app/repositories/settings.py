from datetime import datetime, timezone

def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}
def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))

def list_history(conn, limit=50):
    return [dict(r) for r in conn.execute(
        "SELECT id, field, old_value, new_value, changed_at FROM settings_history ORDER BY id DESC LIMIT ?",
        (limit,)).fetchall()]

def _normalize(field, value):
    """Return (numeric_value, canonical_string). Raise ValueError on invalid input."""
    if field == "coverage":
        try:
            num = float(value)
        except (TypeError, ValueError):
            raise ValueError("默认涂布率必须是数字")
        if num != num or num in (float("inf"), float("-inf")):
            raise ValueError("默认涂布率必须是有限数字")
        if num <= 0:
            raise ValueError("默认涂布率必须大于 0")
        return num, ("%g" % num)
    if field == "coats":
        # reject bool and non-integral values explicitly
        if isinstance(value, bool):
            raise ValueError("默认遍数必须是正整数")
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise ValueError("默认遍数必须是正整数")
        if float(value) != num:
            raise ValueError("默认遍数必须是正整数")
        if num < 1:
            raise ValueError("默认遍数至少为 1")
        return float(num), str(num)
    raise ValueError(f"未知设置项: {field}")

def update_values(conn, changes):
    """Atomically apply changed settings and append one history row per real change.

    Returns the list of inserted history entries. Equal old/new values are skipped.
    Validation runs before the transaction; upsert + history insert commit together.
    """
    parsed = {}
    for field in ("coverage", "coats"):
        if field in changes and changes[field] is not None:
            parsed[field] = _normalize(field, changes[field])
    if not parsed:
        return []
    try:
        conn.execute("BEGIN")
        current = get_map(conn)
        inserted = []
        for field, (num, new_str) in parsed.items():
            old_raw = current.get(field)
            if old_raw is not None:
                try:
                    if float(old_raw) == num:
                        continue  # unchanged: no upsert, no history row
                except ValueError:
                    pass  # corrupt legacy value: treat as a real change
            conn.execute(
                "INSERT INTO settings(key,value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (field, new_str))
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT INTO settings_history(field,old_value,new_value,changed_at) VALUES (?,?,?,?)",
                (field, old_raw, new_str, now))
            inserted.append({"field": field, "old_value": old_raw, "new_value": new_str})
        conn.commit()
        return inserted
    except Exception:
        conn.rollback()
        raise
