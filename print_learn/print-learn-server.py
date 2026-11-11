#!/usr/bin/env python3
"""
Print Bot - kho ma loi tu hoc (auto-learn store)

Chay doc lap canh Home Assistant. Chi dung thu vien chuan cua Python.
Home Assistant goi qua rest_command:
  POST   /learn            {"code": "E999", "text": "noi dung", "group_id": "..."}
  GET    /lookup?code=E999 -> {"found": true, "code": "E999", "text": "..."}
  GET    /list             -> {"count": n, "items": [{code, text, updated_at}, ...]}
  DELETE /learn?code=E999  -> xoa ma da hoc (ban cu van con trong bang history)

Bao mat tuy chon: dat bien moi truong PRINT_BOT_TOKEN, Home Assistant gui kem
header X-Token. Khong dat token thi ai trong LAN cung ghi duoc - chi nen dung
khi mang noi bo tin cay.

Du lieu: SQLite tai PRINT_DB_PATH (mac dinh /data/print_learn.db, khi chay
local thi ./print_learn.db). Moi lan ghi deu luu 1 ban vao bang history de
co the tra cuu / khoi phuc ban truoc.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB_PATH = os.environ.get("PRINT_DB_PATH", "./print_learn.db")
TOKEN = os.environ.get("PRINT_BOT_TOKEN", "")
PORT = int(os.environ.get("PRINT_BOT_PORT", "8765"))


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS learned (
               code TEXT PRIMARY KEY,
               text TEXT NOT NULL,
               group_id TEXT DEFAULT '',
               updated_at TEXT NOT NULL
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS history (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               code TEXT NOT NULL,
               text TEXT NOT NULL,
               group_id TEXT DEFAULT '',
               saved_at TEXT NOT NULL,
               action TEXT NOT NULL DEFAULT 'upsert'
           )"""
    )
    return conn


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        if not TOKEN:
            return True
        return self.headers.get("X-Token", "") == TOKEN

    def _guard(self):
        if self._authorized():
            return True
        self._json(401, {"ok": False, "error": "unauthorized"})
        return False

    def do_GET(self):
        if not self._guard():
            return
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path == "/health":
            self._json(200, {"ok": True})
            return
        if parsed.path == "/lookup":
            code = (qs.get("code", [""])[0] or "").strip().upper()
            if not code:
                self._json(200, {"found": False, "code": "", "text": ""})
                return
            conn = db()
            row = conn.execute(
                "SELECT text, updated_at FROM learned WHERE code = ?", (code,)
            ).fetchone()
            conn.close()
            if row:
                self._json(
                    200,
                    {"found": True, "code": code, "text": row[0], "updated_at": row[1]},
                )
            else:
                self._json(200, {"found": False, "code": code, "text": ""})
            return
        if parsed.path == "/list":
            conn = db()
            rows = conn.execute(
                "SELECT code, text, updated_at FROM learned ORDER BY code"
            ).fetchall()
            conn.close()
            self._json(
                200,
                {
                    "count": len(rows),
                    "items": [
                        {"code": r[0], "text": r[1], "updated_at": r[2]} for r in rows
                    ],
                },
            )
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if not self._guard():
            return
        parsed = urlparse(self.path)
        if parsed.path != "/learn":
            self._json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._json(400, {"ok": False, "error": "invalid json"})
            return
        code = str(data.get("code", "")).strip().upper()
        text = str(data.get("text", "")).strip()
        group_id = str(data.get("group_id", "")).strip()
        if not code or not text:
            self._json(400, {"ok": False, "error": "code and text are required"})
            return
        ts = now_iso()
        conn = db()
        conn.execute(
            "INSERT INTO learned(code, text, group_id, updated_at) VALUES(?,?,?,?) "
            "ON CONFLICT(code) DO UPDATE SET text=excluded.text, "
            "group_id=excluded.group_id, updated_at=excluded.updated_at",
            (code, text, group_id, ts),
        )
        conn.execute(
            "INSERT INTO history(code, text, group_id, saved_at, action) "
            "VALUES(?,?,?,?,'upsert')",
            (code, text, group_id, ts),
        )
        conn.commit()
        conn.close()
        self._json(200, {"ok": True, "code": code, "updated_at": ts})

    def do_DELETE(self):
        if not self._guard():
            return
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if parsed.path != "/learn":
            self._json(404, {"ok": False, "error": "not found"})
            return
        code = (qs.get("code", [""])[0] or "").strip().upper()
        if not code:
            self._json(400, {"ok": False, "error": "code is required"})
            return
        conn = db()
        row = conn.execute(
            "SELECT text, group_id FROM learned WHERE code = ?", (code,)
        ).fetchone()
        conn.execute("DELETE FROM learned WHERE code = ?", (code,))
        if row:
            conn.execute(
                "INSERT INTO history(code, text, group_id, saved_at, action) "
                "VALUES(?,?,?,?,'delete')",
                (code, row[0], row[1], now_iso()),
            )
        conn.commit()
        conn.close()
        self._json(200, {"ok": True, "code": code, "deleted": bool(row)})

    def log_message(self, fmt, *args):
        # Giu log ngan gon
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    db().close()
    print(f"print-learn-server listening on :{PORT}, db={DB_PATH}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
