from typing import Tuple


def test_hospital_icu_endpoint(client):
    response = client.get("/api/v1/hospitals/icu/1")
    assert response.status_code == 200
    data = response.json()
    assert "total_beds" in data
    assert "occupancy_rate" in data


def test_hospital_blood_inventory_endpoint(client):
    response = client.get("/api/v1/hospitals/blood/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
