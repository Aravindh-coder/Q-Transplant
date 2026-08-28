"""Authenticated ESP32 event protocol definitions."""
ESP32_EVENTS = {
    "EMERGENCY": "Emergency raised by hardware",
    "ACKNOWLEDGE": "Emergency acknowledged by hardware",
    "DONOR": "Donor button event",
    "HEARTBEAT": "Device heartbeat",
}
REQUIRED_FIELDS = {"device_id", "event", "timestamp", "nonce"}

def validate_event(payload):
    if not isinstance(payload, dict) or not REQUIRED_FIELDS.issubset(payload):
        raise ValueError("Invalid ESP32 event envelope")
    if payload["event"] not in ESP32_EVENTS:
        raise ValueError("Unsupported ESP32 event")
    return True
