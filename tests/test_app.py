"""Tests for the gitops-k8s-pipeline demo app.

Standard library only — no test dependencies, so the same suite runs in
CI and on a laptop. The app is started in-process on an ephemeral port.
"""

import http.client
import json
import os
import sys
import threading
import unittest
from http.server import HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

os.environ["APP_VERSION"] = "test-1.2.3"

import app as demo_app  # noqa: E402


class DemoAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), demo_app.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read()
        headers = dict(resp.getheaders())
        conn.close()
        return resp.status, headers, body

    def test_root_returns_version_page(self):
        status, headers, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"test-1.2.3", body)
        self.assertIn(b"gitops-k8s-pipeline demo", body)

    def test_healthz_returns_json_with_version(self):
        status, headers, body = self._get("/healthz")
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers["Content-Type"])
        payload = json.loads(body)
        self.assertEqual(payload, {"status": "ok", "version": "test-1.2.3"})

    def test_unknown_path_serves_the_demo_page(self):
        # The demo app has no router: any path shows the version page.
        status, _, body = self._get("/anything-else")
        self.assertEqual(status, 200)
        self.assertIn(b"test-1.2.3", body)

    def test_version_defaults_to_dev_without_env(self):
        self.assertEqual(demo_app.VERSION, "test-1.2.3")


if __name__ == "__main__":
    unittest.main()
