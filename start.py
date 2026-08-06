"""
Guntur Traffic Analytics - Unified Live Application Launcher
Starts both the 30-minute background auto-collector scheduler and the Streamlit Dashboard.
"""

import sys
import time
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

PYTHON_EXE = sys.executable

def main():
    print("=" * 80)
    print("  GUNTUR TRAFFIC ANALYTICS PLATFORM — LIVE LAUNCHER")
    print("=" * 80)
    print("  Starting Background Traffic Collector (Every 30 min)...")

    # Start scheduler in background process
    scheduler_proc = subprocess.Popen(
        [PYTHON_EXE, "scripts/scheduler.py"],
        cwd=str(project_root)
    )

    print("  Scheduler PID:", scheduler_proc.pid)
    print("  Starting Streamlit Analytics Dashboard...")
    print("=" * 80)

    try:
        # Launch Streamlit dashboard in foreground
        streamlit_cmd = [
            PYTHON_EXE, "-m", "streamlit", "run", "dashboard/app.py"
        ]
        subprocess.run(streamlit_cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\nStopping Guntur Traffic Analytics service...")
    finally:
        if scheduler_proc.poll() is None:
            scheduler_proc.terminate()
            scheduler_proc.wait()
            print("Background scheduler stopped.")
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
