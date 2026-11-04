"""Demo app for gitops-k8s-pipeline.

A dependency-free HTTP server (Python standard library only). It serves
one page showing the running version, taken from the APP_VERSION
environment variable so a GitOps image update is visible in the browser.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = os.environ.get("APP_VERSION", "dev")
PORT = int(os.environ.get("PORT", "8000"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - http.server naming
        if self.path == "/healthz":
            body = json.dumps({"status": "ok", "version": VERSION}).encode()
            content_type = "application/json"
        else:
            body = (
                "<!doctype html><html><body>"
                f"<h1>gitops-k8s-pipeline demo</h1>"
                f"<p>Running version: <strong>{VERSION}</strong></p>"
                "<p>Deployed by Argo CD from the prod Kustomize overlay.</p>"
                "</body></html>"
            ).encode()
            content_type = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep container logs readable
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
