#ifndef CONFIG_H
#define CONFIG_H

// WiFi Access Point Credentials
#define WIFI_SSID "QTRANSPLANT_DISPATCH_NET"
#define WIFI_PASS "TransplantSecure2026!"

// Q-Transplant Backend API Telemetry Endpoint
#define BACKEND_HOST "http://192.168.1.100:8000"
#define TELEMETRY_ENDPOINT "/api/v1/telemetry/push"
#define SOS_ENDPOINT "/api/v1/telemetry/emergency-trigger"

// Cold Box Identification & Sensor Pins
#define COLD_BOX_ID "BOX-ESP32-001"
#define DHTPIN 4
#define DHTTYPE DHT22
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17
#define SOS_BUTTON_PIN 0       // BOOT button doubles as SOS
#define LED_ALARM_PIN 2        // Onboard LED for alarm state

// Safe Temperature Threshold
#define TEMP_MIN_OK 2.0
#define TEMP_MAX_OK 8.0

// Telemetry Polling Interval (milliseconds)
#define TELEMETRY_INTERVAL_MS 5000

#endif // CONFIG_H
