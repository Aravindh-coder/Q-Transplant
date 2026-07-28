from backend.app.services.telemetry_service import TelemetryService


def test_telemetry_safe_range():
    is_alarm, msg = TelemetryService.evaluate_cold_box(temp_celsius=4.5, battery_level=90.0)
    assert is_alarm is False
    assert "Nominal" in msg


def test_telemetry_ischemia_alarm():
    is_alarm, msg = TelemetryService.evaluate_cold_box(temp_celsius=11.2, battery_level=80.0)
    assert is_alarm is True
    assert "ISCHEMIA ALERT" in msg


def test_telemetry_freeze_alarm():
    is_alarm, msg = TelemetryService.evaluate_cold_box(temp_celsius=0.5, battery_level=80.0)
    assert is_alarm is True
    assert "FREEZE WARNING" in msg


def test_telemetry_push_endpoint(client):
    payload = {
        "cold_box_id": "BOX-TEST-99",
        "lat": 12.97,
        "lng": 77.59,
        "temp_celsius": 4.2,
        "humidity_percent": 80.0,
        "battery_level": 95.0
    }
    res = client.post("/api/v1/telemetry/push", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["cold_box_id"] == "BOX-TEST-99"
