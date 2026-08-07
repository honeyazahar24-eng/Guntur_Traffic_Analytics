"""
Guntur Traffic Analytics - Scheduler
Collects traffic data every 30 minutes and logs status to a JSON file.
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
import json
import schedule
import traceback
from datetime import datetime, timezone, timedelta

ist_tz = timezone(timedelta(hours=5, minutes=30))


from scripts.collector import main as collect_data

STATUS_FILE = project_root / "logs" / "scheduler_status.json"
STATUS_FILE.parent.mkdir(exist_ok=True)


def write_status(status: str, message: str, last_count: int = 0):
    now_ist = datetime.now(ist_tz)
    data = {
        "status": status,
        "message": message,
        "last_run": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
        "last_record_count": last_count,
        "next_run": schedule.next_run().strftime("%Y-%m-%d %H:%M:%S IST") if schedule.next_run() else "N/A"
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def read_db_count():
    """Return current total record count from database."""
    try:
        from database.database import TrafficDatabase
        db = TrafficDatabase()
        db.cursor.execute("SELECT COUNT(*) FROM traffic_data")
        count = db.cursor.fetchone()[0]
        db.close()
        return count
    except Exception:
        return 0


def run_collection():
    started_at = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M:%S IST")
    print(f"\n{'='*80}")
    print(f"  COLLECTION STARTED: {started_at}")
    print(f"{'='*80}")

    write_status("running", f"Collection in progress since {started_at}")


    try:
        collect_data()
        count = read_db_count()
        msg = f"Last successful run at {started_at} — {count} total records"
        write_status("success", msg, count)
        print(f"\n  Collection completed successfully. Total records: {count}")

    except Exception as e:
        err = traceback.format_exc()
        write_status("error", f"Collection failed at {started_at}: {e}")
        print(f"\n  Collection FAILED:\n{err}")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*80)
    print("  GUNTUR TRAFFIC ANALYTICS  —  AUTO SCHEDULER")
    print("="*80)
    # Schedule at :00 and :30 of every hour (e.g., 11:00, 11:30, 12:00, 12:30...)
    schedule.every().hour.at(":00").do(run_collection)
    schedule.every().hour.at(":30").do(run_collection)

    print("  Interval  : Every 30 minutes at top/half hour (:00 & :30)")
    print("  Next run  : ", schedule.next_run())
    print("  Press Ctrl+C to stop")
    print("="*80 + "\n")

    # Initial collection on startup
    run_collection()


    while True:
        schedule.run_pending()
        # Update next_run in status file
        try:
            if STATUS_FILE.exists():
                with open(STATUS_FILE) as f:
                    data = json.load(f)
                if schedule.next_run():
                    data["next_run"] = schedule.next_run().strftime("%Y-%m-%d %H:%M:%S")
                with open(STATUS_FILE, "w") as f:
                    json.dump(data, f, indent=2)
        except Exception:
            pass
        time.sleep(5)