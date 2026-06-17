from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
import time
from urllib.parse import urlparse


def _tag_payload() -> dict[str, object]:
    now = time.time()
    tags = [
        {
            "epc": "E2000017221101441890ABCD",
            "rssi_dbm": -48.5,
            "antenna": 1,
            "frequency_khz": 915250,
            "read_count": 42,
            "in_range": True,
            "last_seen": now,
            "name": "demo-tag",
        },
        {
            "epc": "E2000017221101441890DCBA",
            "rssi_dbm": -71.0,
            "antenna": 1,
            "frequency_khz": 915750,
            "read_count": 8,
            "in_range": False,
            "last_seen": now - 12,
            "name": "old-tag",
        },
    ]
    return {
        "ok": True,
        "tags": tags,
        "tag_count": len(tags),
        "active_count": sum(1 for tag in tags if tag["in_range"]),
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/")
        payload = _tag_payload()

        if path == "/api/v1/tags":
            self._send_json(payload)
            return

        if path == "/api/v1/tags/active":
            active = [tag for tag in payload["tags"] if tag["in_range"]]
            self._send_json({"ok": True, "tags": active})
            return

        if path.startswith("/api/v1/tags/"):
            epc = path.rsplit("/", 1)[-1].lower()
            for tag in payload["tags"]:
                if epc in str(tag["epc"]).lower():
                    self._send_json({"ok": True, "tag": tag})
                    return
            self._send_json({"ok": False, "error": "not found"}, status=404)
            return

        if path == "/api/v1/reader/status":
            self._send_json(
                {
                    "ok": True,
                    "reader_host": "mock",
                    "device_id": "mock-rfid-reader",
                    "reader_started": True,
                    "stream": {"connected": True},
                    "tag_count": payload["tag_count"],
                    "active_count": payload["active_count"],
                }
            )
            return

        self._send_json({"ok": False, "error": "not found"}, status=404)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a mock RFID HTTP API")
    parser.add_argument("--host", default="127.0.0.1", help="Host/interface to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Mock RFID API listening on http://{args.host}:{args.port}/api/v1")
    server.serve_forever()


if __name__ == "__main__":
    main()
