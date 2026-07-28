# ESP32 Microcontroller Cold-Box Telemetry Integration Guide

## Payload Specification (`POST /api/v1/telemetry/push`)
ESP32 devices send a JSON HTTP POST payload every 5 seconds:

```json
{
  "cold_box_id": "BOX-ESP32-001",
  "lat": 12.8945,
  "lng": 77.5989,
  "temp_celsius": 4.2,
  "humidity_percent": 82.5,
  "battery_level": 95.0
}
```

## Alarm Conditions
1. **Temperature Freeze Alert**: `temp_celsius < 2.0°C`
2. **Ischemia Alert**: `temp_celsius > 8.0°C`
3. **Power Warning**: `battery_level < 15.0%`
