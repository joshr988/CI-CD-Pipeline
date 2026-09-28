import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen
from unittest.mock import patch

from app import Handler


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health(self):
        with urlopen(self.url + "/health", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "application/json")
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_version_identifies_release(self):
        with patch.dict("os.environ", {"APP_REVISION": "abc123"}):
            with urlopen(self.url + "/version", timeout=5) as response:
                self.assertEqual(json.load(response), {"revision": "abc123"})

    def test_unknown_route(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.url + "/missing", timeout=5)
        self.assertEqual(caught.exception.code, 404)
        self.assertEqual(json.load(caught.exception), {"error": "not found"})
        caught.exception.close()
