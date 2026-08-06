"""
Root entry point redirect for Streamlit Cloud deployment.
Allows both 'app.py' and 'dashboard/app.py' to be used as Main file path.
"""

import sys
from pathlib import Path

root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

dashboard_path = root / "dashboard"
if str(dashboard_path) not in sys.path:
    sys.path.insert(0, str(dashboard_path))

# Run dashboard app
import dashboard.app
