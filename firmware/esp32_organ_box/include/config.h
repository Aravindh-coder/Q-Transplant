#ifndef CONFIG_H
#define CONFIG_H

// ==============================================================================
// Q-TRANSPLANT ESP32 DEVKIT HARDWARE CONFIGURATION & PIN MAPPING
// ==============================================================================

// WiFi Credentials (Update with your local Wi-Fi SSID and Password)
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASS "YOUR_WIFI_PASSWORD"

// Q-Transplant Server Host IP (Replace with your laptop/server IP address)
#define BACKEND_HOST "http://192.168.1.100:8080"  // e.g. http://192.168.1.50:8080

// API Endpoints
#define TELEMETRY_ENDPOINT "/api/v1/telemetry/push"
#define EMERGENCY_ENDPOINT "/api/v1/emergency/dispatch"
#define MATCH_ENDPOINT     "/api/v1/matches/"

// Cold Box Unique Identification
#define COLD_BOX_ID "BOX-ESP32-001"

// ------------------------------------------------------------------------------
// EXACT HARDWARE PIN MAPPINGS
// ------------------------------------------------------------------------------
#define OLED_SDA_PIN    21  // OLED I2C Data
#define OLED_SCL_PIN    22  // OLED I2C Clock
#define OLED_RESET      -1  // Reset pin (-1 if sharing ESP32 reset)
#define SCREEN_WIDTH   128  // OLED display width in pixels
#define SCREEN_HEIGHT   64  // OLED display height in pixels
#define OLED_I2C_ADDR 0x3C  // Standard I2C address for SSD1306

// Buttons (INPUT_PULLUP: Pressed = LOW)
#define BTN_EMERGENCY   13  // Red Emergency Button
#define BTN_DONOR       12  // Blue/Yellow Donor Available Button
#define BTN_ACKNOWLEGE  14  // White/Green Acknowledge Button

// Actuators & Indicators
#define LED_GREEN       18  // Green System Status LED
#define LED_RED         19  // Red Alert / Alarm LED
#define BUZZER_PIN      23  // Active Buzzer

// Telemetry Timing & Thresholds
#define TELEMETRY_INTERVAL_MS 4000  // Push telemetry every 4 seconds
#define TEMP_SAFE_MIN 2.0
#define TEMP_SAFE_MAX 8.0

#endif // CONFIG_H
