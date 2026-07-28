# ESP32 Organ Transport Cold-Box Telemetry Module

This directory contains the PlatformIO/C++ firmware for the **Q-Transplant Cold-Box Telemetry Unit**.

## Features
- **DHT22 Temperature & Humidity Sensor**: Monitors cold-chain preservation temperature (safe threshold 2.0°C to 8.0°C).
- **Neo-6M GPS Module**: Provides real-time latitude/longitude coordinates of ambulance organ transit.
- **LiPo Battery Monitor**: Reports battery power backup level.
- **HTTP REST / JSON Push**: Periodically posts telemetry payloads to `/api/v1/telemetry/push`.

## Wiring Diagram

| ESP32 Pin | Peripheral Pin | Component |
|-----------|----------------|-----------|
| GPIO 4    | DATA           | DHT22 Temp/Humidity |
| GPIO 16   | TXD            | Neo-6M GPS RX |
| GPIO 17   | RXD            | Neo-6M GPS TX |
| 3.3V      | VCC            | Sensors |
| GND       | GND            | Common Ground |

## Flashing Instructions
```bash
# Using PlatformIO CLI
cd firmware/esp32_organ_box
pio run --target upload
pio device monitor
```
