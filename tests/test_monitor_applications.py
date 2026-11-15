"""Synthetic boundary cases; none of these are real application outcomes."""
import importlib.util
from datetime import date
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("monitor", Path(__file__).resolve().parents[1] / "scripts/monitor_applications.py")
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class MonitoringTests(unittest.TestCase):
    def row(self, **changes):
        return {"id": "test-1", "offer_id": "test-offer", "company": "Synthetic", "title": "Test", "sent_at": "2026-11-04", "status": "sent", "response_at": "", **changes}

    def test_threshold_inclusive(self):
        self.assertEqual(len(monitor.check([self.row()], date(2026, 11, 14))["alerts"]), 1)
        self.assertEqual(monitor.check([self.row()], date(2026, 11, 13))["alerts"], [])

    def test_answered_and_withdrawn_are_not_reminders(self):
        for row in [self.row(status="response", response_at="2026-11-05"), self.row(status="withdrawn")]:
            self.assertEqual(monitor.check([row], date(2026, 11, 14))["alerts"], [])

    def test_bad_dates_status_and_duplicates_are_errors(self):
        for row in [self.row(sent_at="2026-11-31"), self.row(sent_at="2026-11-15"), self.row(status="interview"), self.row(response_at="2026-11-02"), self.row(status="unknown")]:
            self.assertEqual(len(monitor.check([row], date(2026, 11, 14))["data_errors"]), 1)
        self.assertEqual(len(monitor.check([self.row(), self.row()], date(2026, 11, 14))["data_errors"]), 1)

    def test_empty_tracker_is_not_an_alert(self):
        self.assertEqual(monitor.check([], date(2026, 11, 14)), {"n_applications": 0, "alerts": [], "data_errors": []})


if __name__ == "__main__":
    unittest.main()
