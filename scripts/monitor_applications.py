"""Check private application CSV; append a dated, local-only monitoring record."""
import argparse
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["id", "offer_id", "company", "title", "sent_at", "status", "response_at"]
STATUSES = {"sent", "response", "interview", "rejected", "accepted", "withdrawn"}


def check(rows, today, threshold=10):
    alerts = []
    errors = []
    seen = set()
    for index, row in enumerate(rows, start=2):
        try:
            if any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS[:-1]):
                raise ValueError("missing required field")
            if row["id"] in seen:
                raise ValueError("duplicate application id")
            seen.add(row["id"])
            if row["status"] not in STATUSES:
                raise ValueError("unknown status")
            sent = date.fromisoformat(row["sent_at"])
            if sent.isoformat() != row["sent_at"] or sent > today:
                raise ValueError("invalid or future sending date")
            response = date.fromisoformat(row["response_at"]) if row.get("response_at") else None
            if response and (response.isoformat() != row["response_at"] or not sent <= response <= today):
                raise ValueError("response date outside sending date / today range")
            if row["status"] in {"response", "interview", "rejected", "accepted"} and not response:
                raise ValueError("response date required for this status")
            if row["status"] == "sent" and response:
                raise ValueError("sent status inconsistent with recorded response")
            age = (today - sent).days
            if row["status"] == "sent" and not response and age >= threshold:
                alerts.append({"application_id": row["id"], "company": row["company"], "days_waiting": age})
        except (ValueError, TypeError) as exc:
            errors.append({"line": index, "error": str(exc)})
    return {"n_applications": len(rows), "alerts": alerts, "data_errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/applications/applications.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/monitoring")
    parser.add_argument("--threshold", type=int, default=10)
    parser.add_argument("--init", action="store_true", help="create an empty tracker if missing")
    args = parser.parse_args()
    if args.threshold < 1:
        parser.error("threshold must be positive")
    if args.init and not args.input.exists():
        args.input.parent.mkdir(parents=True, exist_ok=True)
        with args.input.open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerow(FIELDS)
    if not args.input.exists():
        parser.error("tracker missing: export the dashboard CSV here, or run with --init")
    try:
        with args.input.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != FIELDS:
                parser.error("unexpected CSV columns; use the dashboard CSV export")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        parser.error(str(exc))
    now = datetime.now(timezone.utc)
    # The user's project timezone determines calendar-day reminder thresholds.
    try:
        from zoneinfo import ZoneInfo
        today = now.astimezone(ZoneInfo("Europe/Paris")).date()
    except (ImportError, KeyError):
        # Windows Python may lack IANA timezone data; derive Paris DST with EU rules.
        from calendar import monthrange
        from datetime import timedelta
        def last_sunday(month):
            last = date(now.year, month, monthrange(now.year, month)[1])
            return last - timedelta(days=(last.weekday() + 1) % 7)
        start = datetime.combine(last_sunday(3), datetime.min.time(), timezone.utc).replace(hour=1)
        end = datetime.combine(last_sunday(10), datetime.min.time(), timezone.utc).replace(hour=1)
        today = (now + timedelta(hours=2 if start <= now < end else 1)).date()
    result = {
        "run_at": now.isoformat(), "check_date": today.isoformat(),
        "rule": f"sent without response for at least {args.threshold} calendar days",
        "input": str(args.input.resolve()), **check(rows, today, args.threshold),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "history.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False) + "\n")
    (args.output_dir / "latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {len(rows)} applications: {len(result['alerts'])} reminder(s), {len(result['data_errors'])} data error(s).")
    print(f"History: {args.output_dir / 'history.jsonl'}")
    return 1 if result["data_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
