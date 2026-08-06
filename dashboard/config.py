from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "database" / "traffic.db"

REPORTS_PATH = PROJECT_ROOT / "reports"

# ==========================================================
# APPLICATION
# ==========================================================

APP_TITLE = "Guntur Traffic Analytics Platform"

PAGE_ICON = "🚦"

LAYOUT = "wide"

INITIAL_SIDEBAR_STATE = "expanded"

APP_VERSION = "2.0.0"

# ==========================================================
# TABLES
# ==========================================================

DEFAULT_RECORD_LIMIT = 20

TABLE_HEIGHT = 450

# ==========================================================
# CHARTS
# ==========================================================

CHART_HEIGHT = 420

CHART_TEMPLATE = "plotly_white"

CHART_MARGIN = dict(
    l=20,
    r=20,
    t=50,
    b=20
)

# ==========================================================
# TRAFFIC THRESHOLDS
# ==========================================================

NORMAL_SPEED = 40

MODERATE_SPEED = 25

# ==========================================================
# COLORS
# ==========================================================

PRIMARY = "#1976D2"

SUCCESS = "#2E7D32"

WARNING = "#F9A825"

DANGER = "#D32F2F"

BACKGROUND = "#F5F7FA"