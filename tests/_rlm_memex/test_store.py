import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from rlm_memex import MemexStore
from rlm_memex.engine import run
from rlm_memex.store import import_catalog, verify_handoff


class MemexTests(unittest.TestCase):
    def setUp(self):
        self.store = MemexStore(":memory:")

    def tearDown(self):
        self.store.close()

    def put(self, namespace="tools", body="Heat flow solver", version="1"):
        return self.store.put(namespace, "same-id", version, "Thermal", body, "fixture")

    def test_namespace_and_version_separation(self):
        self.put()
        self.put("parts", "Heat exchanger")
        self.put(version="2", body="Improved heat solver")
        self.assertEqual(len(self.store.search("heat", "tools")), 2)
        self.assertEqual(len(self.store.search("heat", "parts")), 1)
        self.assertEqual(self.store.read("tools", "same-id", "1")["body"], "Heat flow solver")

    def test_versions_are_immutable_and_import_idempotent(self):
        self.assertTrue(self.put())
        self.assertFalse(self.put())
        with self.assertRaises(ValueError):
            self.put(body="Changed data")

    def test_read_is_bounded_and_reconstructable(self):
        original = "Ω flow " * 2000
        self.put(body=original)
        start = 0
        chunks = []
        while start is not None:
            page = self.store.read("tools", "same-id", "1", start, 501)
            chunks.append(page["body"])
            start = page["next_start"]
        self.assertEqual("".join(chunks), original)
        with self.assertRaises(ValueError):
            self.store.read("tools", "same-id", "1", size=999999)

    def test_search_literalizes_fts_syntax(self):
        self.put()
        self.assertEqual(self.store.search('" OR () -- heat', "tools")[0]["id"], "same-id")
        self.assertEqual(self.store.search("()", "tools"), [])

    def test_duplicate_catalog_rolls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "parts.json"
            path.write_text(json.dumps([{"id": "x"}, {"id": "x"}]))
            with self.assertRaises(ValueError):
                import_catalog(self.store, path, "parts", "1")
        self.assertEqual(self.store.stats(), {})

    def test_draft_handoff_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "manifest.json").write_text('{"release_status":"draft"}')
            with self.assertRaises(ValueError):
                verify_handoff(directory)

    def test_payload_limit_fails_without_silent_truncation(self):
        self.put(body="x" * 500)
        with self.assertRaises(ValueError):
            self.store.context(max_chars=100)

    def test_adapter_keeps_corpus_out_of_root_prompt(self):
        self.put(body="External evidence " * 10000)
        captured = {}

        class FakeRLM:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def completion(self, payload, root_prompt):
                captured["payload"] = payload
                captured["question"] = root_prompt
                return SimpleNamespace(response="test")

        result = run(self.store, "Which solver?", "test-model", factory=FakeRLM)
        self.assertEqual(result.response, "test")
        self.assertEqual(captured["environment"], "docker")
        self.assertGreater(captured["max_depth"], 1)
        self.assertEqual(captured["question"], "Which solver?")
        self.assertGreater(len(str(captured["payload"])), 100000)


if __name__ == "__main__":
    unittest.main()
