import requests

BASE_URL = "http://ais-api:8000"


def get_vessels():
    return requests.get(f"{BASE_URL}/vessels").json()


def get_positions_by_mmsi(mmsi):
    return requests.get(f"{BASE_URL}/positions").json()


def get_latest_positions():
    return requests.get(f"{BASE_URL}/vessels/latest").json()


def get_collision_alerts():
    return requests.get(f"{BASE_URL}/collision-alerts").json()


