import os
import json
import requests
from dotenv import load_dotenv

# Load API Key
load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={API_KEY}"

headers = {
    "Content-Type": "application/json",
    "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
}

payload = {
    "origin": {
        "location": {
            "latLng": {
                "latitude": 16.3069,
                "longitude": 80.4365
            }
        }
    },
    "destination": {
        "location": {
            "latLng": {
                "latitude": 16.3052,
                "longitude": 80.4428
            }
        }
    },
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE"
}

response = requests.post(
    url,
    headers=headers,
    json=payload
)

print(response.status_code)
print(json.dumps(response.json(), indent=4))