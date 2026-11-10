"""Anonymous impact metrics. No names, no resume text, no IPs: only an event kind,
a random per-browser id, the language, and a number (e.g. a resume score).

Uses Postgres when DATABASE_URL is set (survives restarts on free hosting),
otherwise a local SQLite file."""
from __future__ import annotations

import os
import re
import sqlite3
import threading
import time

KINDS = {"visit", "resume_check", "opportunities", "roadmap", "interview_answer",
         "chat", "outbound_click", "feedback_up", "feedback_down"}
_SID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


class Metrics:
    def __init__(self, database_url: str | None = None, sqlite_path: str | None = None):
        self.lock = threading.Lock()
        self.pg = bool(database_url)
        if self.pg:
            import psycopg  # type: ignore

            self.conn = psycopg.connect(database_url, autocommit=True)
        else:
            path = sqlite_path or os.getenv("METRICS_DB", "kaamsaathi_metrics.db")
            self.conn = sqlite3.connect(path, check_same_thread=False)
        self._exec(
            "CREATE TABLE IF NOT EXISTS events (ts DOUBLE PRECISION, kind TEXT, sid TEXT, lang TEXT, "
            "value DOUBLE PRECISION, ref TEXT)"
        )

    def _exec(self, sql: str, params: tuple = ()):
        if self.pg:
            sql = sql.replace("?", "%s")
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            if not self.pg:
                self.conn.commit()
            return rows

    def record(self, kind: str, sid: str | None, lang: str = "en", value: float | None = None, ref: str = ""):
        if kind not in KINDS:
            return
        sid = sid if sid and _SID_RE.match(sid) else "anon"
        self._exec("INSERT INTO events VALUES (?,?,?,?,?,?)",
                   (time.time(), kind, sid, (lang or "en")[:5], value, (ref or "")[:64]))

    def summary(self) -> dict:
        def one(sql, params=()):
            r = self._exec(sql, params)
            return r[0][0] if r and r[0][0] is not None else 0

        counts = {k: one("SELECT COUNT(*) FROM events WHERE kind=?", (k,)) for k in sorted(KINDS)}
        people = one("SELECT COUNT(DISTINCT sid) FROM events WHERE sid<>'anon'")
        langs = {row[0]: row[1] for row in self._exec(
            "SELECT lang, COUNT(DISTINCT sid) FROM events WHERE sid<>'anon' GROUP BY lang")}
        # before/after: people who checked their resume 2+ times, first vs best later score
        rows = self._exec(
            "SELECT sid, ts, value FROM events WHERE kind='resume_check' AND sid<>'anon' ORDER BY sid, ts")
        by_sid: dict[str, list[float]] = {}
        for sid, _ts, v in rows:
            by_sid.setdefault(sid, []).append(float(v or 0))
        rechecks = {s: v for s, v in by_sid.items() if len(v) >= 2}
        improved = [max(v[1:]) - v[0] for v in rechecks.values()]
        first_ts = one("SELECT MIN(ts) FROM events")
        return {
            "people": people,
            "events": counts,
            "languages": langs,
            "resume_rechecked_by": len(rechecks),
            "resume_improved_by": sum(1 for d in improved if d > 0),
            "avg_resume_score_gain": round(sum(improved) / len(improved), 1) if improved else 0,
            "helpful_votes": counts["feedback_up"],
            "not_helpful_votes": counts["feedback_down"],
            "since": time.strftime("%Y-%m-%d", time.gmtime(first_ts)) if first_ts else None,
            "storage": "postgres" if self.pg else "sqlite",
        }
