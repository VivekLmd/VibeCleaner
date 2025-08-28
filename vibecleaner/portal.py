import sys
import time
import urllib.parse
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

from .telemetry import runs_base_dir
from .report import latest_run_id


WEB_DIR = Path(__file__).resolve().parent / "web"


def _guess_run_id(query: str | None) -> Optional[str]:
    if not query:
        return latest_run_id()
    params = urllib.parse.parse_qs(query)
    rid = params.get("run", [None])[0]
    if rid:
        return rid
    use_latest = params.get("latest", ["0"])[0] in ("1", "true", "TRUE")
    return latest_run_id() if use_latest else None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._serve_file(WEB_DIR / "index.html", content_type="text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            rel = parsed.path.replace("/static/", "")
            target = (WEB_DIR / rel).resolve()
            if not str(target).startswith(str(WEB_DIR)) or not target.exists():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            if target.suffix == ".css":
                ctype = "text/css; charset=utf-8"
            elif target.suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            elif target.suffix == ".svg":
                ctype = "image/svg+xml; charset=utf-8"
            else:
                ctype = "application/octet-stream"
            self._serve_file(target, content_type=ctype)
            return
        if parsed.path == "/events":
            self._serve_events(parsed.query)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _serve_file(self, path: Path, content_type: str):
        try:
            data = path.read_bytes()
        except Exception:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_events(self, query: str | None):
        run_id = _guess_run_id(query)
        if not run_id:
            self.send_error(HTTPStatus.NOT_FOUND, "No run found")
            return
        events_path = runs_base_dir() / run_id / "events.jsonl"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last_size = 0
        # Send a hello event
        self.wfile.write(b"event: hello\n")
        self.wfile.write(f"data: {{\"run_id\": \"{run_id}\"}}\n\n".encode("utf-8"))
        self.wfile.flush()
        try:
            # Stream updates for up to 30 minutes or until client disconnects
            start = time.time()
            while time.time() - start < 1800:
                if not events_path.exists():
                    time.sleep(1.0)
                    continue
                size = events_path.stat().st_size
                if size > last_size:
                    chunk = events_path.read_text(encoding="utf-8")[last_size:]
                    last_size = size
                    for line in chunk.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        payload = f"data: {line}\n\n".encode("utf-8")
                        self.wfile.write(payload)
                    self.wfile.flush()
                # heartbeat
                self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
                time.sleep(1.0)
        except Exception:
            # client disconnected or server shutting down
            pass


def serve(port: int = 8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Portal running at http://127.0.0.1:{port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

