
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")
BASE_URL = "https://api.fortyguard.com"


def get_environmental_parameters(
    latitude,
    longitude,
    temperature,
    date,
    start_time="14:00"
):
    url = f"{BASE_URL}/v1/env_params"

    headers = {
        "api-key": API_KEY
    }

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature": temperature,
        "date_time": {
            "start_date": date,
            "start_time": start_time,
            "filter_type": 1
        },
        "analysis": [
            "heat_index_celsius",
            "apparent_temperature_celsius",
            "relative_humidity_percent"
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()



def check_activity_status(activity_id):
    url = f"{BASE_URL}/v1/status/{activity_id}"

    headers = {
        "api-key": API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    response.raise_for_status()
    return response.json()



def create_heatmap(polygon, date, start_time="14:00", granularity=100):
    url = f"{BASE_URL}/v1/heatmap"

    headers = {
        "api-key": API_KEY
    }

    payload = {
        "polygon_aoi": polygon,
        "date_time": {
            "start_date": date,
            "start_time": start_time,
            "filter_type": 1
        },
        "granularity": granularity
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()



def get_temperature_aware_route(origin, destination, departure_time):
    url = f"{BASE_URL}/v1/routing"

    headers = {"api-key": API_KEY}

    payload = {
        "origin": origin,
        "destination": destination,
        "departure_time": departure_time
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()
