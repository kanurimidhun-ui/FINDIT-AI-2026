import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from model import ItemReport, MatchingEngine
from tools import load_reports, save_reports


def report(report_type="lost", **overrides):
    values = {
        "item_id": "item-1",
        "title": "Blue wallet",
        "description": "blue leather wallet with silver clasp",
        "category": "Wallets",
        "location": "Riverside Park",
        "report_type": report_type,
        "reported_at": datetime(2026, 10, 1),
    }
    values.update(overrides)
    return ItemReport(**values)


class MatchingEngineTests(unittest.TestCase):
    def test_identical_opposite_report_scores_full_match(self):
        engine = MatchingEngine()
        found = report("found", item_id="item-2")
        engine.add_report(found)

        matches = engine.find_matches(report())

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].item_id, "item-2")
        self.assertEqual(matches[0].score, 1.0)

    def test_same_report_type_is_not_a_match(self):
        engine = MatchingEngine()
        engine.add_report(report("lost", item_id="item-2"))

        self.assertEqual(engine.find_matches(report()), [])

    def test_score_uses_description_category_location_and_date(self):
        engine = MatchingEngine()
        target = report()
        comparison = report(
            "found",
            item_id="item-2",
            reported_at=target.reported_at + timedelta(days=30),
        )

        self.assertAlmostEqual(engine._calculate_score(target, comparison), 0.92)


class ReportStorageTests(unittest.TestCase):
    def test_reports_round_trip_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports.json"
            save_reports(path, [report().model_dump(mode="json")])

            loaded = load_reports(path)

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["item_id"], "item-1")
            self.assertEqual(loaded[0]["reported_at"], "2026-10-01T00:00:00")


if __name__ == "__main__":
    unittest.main()
