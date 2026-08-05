from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from oric_memory_tests.cli import verify_manifest, write_manifest


ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def test_repository_manifest_is_current(self):
        self.assertGreater(verify_manifest(ROOT), 0)

    def test_manifest_covers_the_package_and_excludes_caches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "nested").mkdir()
            (root / "nested" / "data.txt").write_text("data\n", encoding="utf-8")
            (root / "source.py").write_text("print('ok')\n", encoding="utf-8")
            (root / ".pytest_cache").mkdir()
            (root / ".pytest_cache" / "ignored").write_text("cache", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "ignored.pyc").write_bytes(b"cache")

            manifest = write_manifest(root)
            content = manifest.read_text(encoding="utf-8")

            self.assertIn("nested/data.txt", content)
            self.assertIn("source.py", content)
            self.assertNotIn(".pytest_cache", content)
            self.assertNotIn("__pycache__", content)
            self.assertEqual(verify_manifest(root), 2)

    def test_verification_detects_modified_and_unlisted_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tracked = root / "tracked.txt"
            tracked.write_text("initial\n", encoding="utf-8")
            write_manifest(root)

            tracked.write_text("modified\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "modifiés=tracked.txt"):
                verify_manifest(root)

            tracked.write_text("initial\n", encoding="utf-8")
            (root / "new.txt").write_text("new\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non_listés=new.txt"):
                verify_manifest(root)


if __name__ == "__main__":
    unittest.main()
