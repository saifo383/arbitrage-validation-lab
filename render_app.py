from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STATE = {
    "service": "arbitrage-validation-lab",
    "mode": "paper-only",
    "real_orders": False,
    "scan_status": "starting",
    "scan_exit_code": None,
    "scan_started_ms": None,
    "scan_ended_ms": None,
    "last_log": None,
}
LOCK = threading.Lock()


def snapshot():
    with LOCK:
        data = dict(STATE)
    summary = Path("paper_summary.json")
    if summary.exists():
        try:
            data["summary"] = json.loads(summary.read_text(encoding="utf-8"))
        except Exception as exc:
            data["summary_read_error"] = str(exc)
    return data


def run_scan():
    with LOCK:
        STATE["scan_status"] = "running"
        STATE["scan_started_ms"] = int(time.time() * 1000)
    env = os.environ.copy()
    process = subprocess.Popen(
        [sys.executable, "binance_live.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )
    assert process.stdout is not None
    for line in process.stdout:
        line = line.rstrip()
        print(line, flush=True)
        with LOCK:
            STATE["last_log"] = line[-2000:]
    code = process.wait()
    with LOCK:
        STATE["scan_exit_code"] = code
        STATE["scan_ended_ms"] = int(time.time() * 1000)
        STATE["scan_status"] = "completed" if code == 0 else "failed"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/status", "/healthz", "/summary"):
            body = json.dumps(snapshot(), indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        print("http:", fmt % args, flush=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    thread = threading.Thread(target=run_scan, name="paper-scan", daemon=True)
    thread.start()
    print(json.dumps({"type": "HTTP_START", "port": port, "real_orders": False}), flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
