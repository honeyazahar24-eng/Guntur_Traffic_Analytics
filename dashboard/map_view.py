import streamlit as st
import pandas as pd
from pathlib import Path


class MapView:
    """Helper module to display saved corridor maps in Streamlit."""

    @staticmethod
    def show_corridor_map(corridor_id: int, direction: str = "Forward"):
        project_root = Path(__file__).resolve().parent.parent
        maps_dir = project_root / "maps"
        map_filename = f"Corridor_{corridor_id:02d}_{direction}.html"
        map_path = maps_dir / map_filename

        if map_path.exists():
            with open(map_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=500, scrolling=True)
        else:
            st.warning(f"Map file not found: `{map_filename}`. Run `python scripts/route_validator.py` to generate map files.")
