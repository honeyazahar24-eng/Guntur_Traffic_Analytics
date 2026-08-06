import os
import requests

from dotenv import load_dotenv

load_dotenv()


class GoogleRoutesService:

    def __init__(self):

        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
            except Exception:
                pass

        self.url = (
            f"https://routes.googleapis.com/directions/v2:computeRoutes"
            f"?key={self.api_key}"
        )

        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": (
                "routes.distanceMeters,"
                "routes.duration,"
                "routes.polyline.encodedPolyline"
            )
        }

    def get_route_data(self, route):

        payload = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": float(route["Origin_Lat"]),
                        "longitude": float(route["Origin_Lng"])
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": float(route["Destination_Lat"]),
                        "longitude": float(route["Destination_Lng"])
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE"
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            print("Google API Error")
            print(response.text)
            return None

        return response.json()