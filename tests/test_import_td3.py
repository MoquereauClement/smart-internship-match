import importlib.util
import tempfile
import csv
import json
import subprocess
import sys
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("td3", Path(__file__).resolve().parents[1] / "scripts/import_td3.py")
td3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td3)


class TD3Tests(unittest.TestCase):
    def test_merge_preserves_legacy_rows_without_publishable_flag(self):
        script = Path(__file__).resolve().parents[1] / "scripts/merge_offer_sources.py"
        with tempfile.TemporaryDirectory() as directory:
            offers_dir = Path(directory) / "data/offers"
            offers_dir.mkdir(parents=True)
            legacy = {"id": "old", "source": "indeed", "description": "Original text"}
            (offers_dir / "merged_offers.json").write_text(json.dumps({"offers": [legacy]}), encoding="utf-8")
            (offers_dir / "td3_offers.json").write_text(json.dumps({"offers": [{"id": "new", "source": "td3_sample", "publishable": False}]}), encoding="utf-8")
            subprocess.run([sys.executable, "-B", str(script)], cwd=directory, check=True, capture_output=True)
            result = json.loads((offers_dir / "merged_offers.json").read_text(encoding="utf-8"))["offers"]
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], legacy)
            self.assertTrue((offers_dir / "merged_offers.json.bak").exists())

    def test_skill_boundaries(self):
        self.assertEqual(td3.mentioned_skills("JavaScript, GitHub and C#"), ["JavaScript", "C#"])
        self.assertEqual(td3.mentioned_skills("C++ and Unity 3D"), ["C++", "Unity"])

    def test_original_platform_and_private_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["id", "site", "title", "description", "company", "location"])
                writer.writeheader()
                row = {"id": "example", "site": "linkedin", "title": "Test", "description": "Python", "company": "Example", "location": "Paris"}
                writer.writerow(row)
                writer.writerow(row)
            offers = td3.load_csv(path)
        self.assertEqual(len(offers), 1)
        self.assertEqual(offers[0]["source"], "td3_sample")
        self.assertEqual(offers[0]["source_site"], "linkedin")
        self.assertFalse(offers[0]["publishable"])
        self.assertEqual(offers[0]["required_skills"], ["Python"])
        self.assertIsNone(offers[0]["experience_required"])
        self.assertEqual(offers[0]["responsibilities"], [])


if __name__ == "__main__":
    unittest.main()
