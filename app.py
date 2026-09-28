"""Small delivery demo API; no third-party runtime dependencies."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            "/health": {"status": "ok"},
            "/version": {"revision": os.environ.get("APP_REVISION", "local")},
        }
        status = 200 if self.path in routes else 404
        body = json.dumps(routes.get(self.path, {"error": "not found"})).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(json.dumps({"event": "http_request", "message": format % args}), flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
