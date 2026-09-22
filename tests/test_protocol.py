import hashlib
import tempfile
import unittest
from pathlib import Path

from app.main import sha256_file


class ProtocolSmokeTests(unittest.TestCase):
    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"directdrop")
            expected = hashlib.sha256(b"directdrop").hexdigest()
            self.assertEqual(sha256_file(path), expected)

    def test_unique_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            module = __import__("app.main", fromlist=["_unique"])
            first = Path(directory) / "file.txt"
            first.write_text("one")
            second = module._unique(first)
            self.assertEqual(second.name, "file (1).txt")


if __name__ == "__main__":
    unittest.main()
