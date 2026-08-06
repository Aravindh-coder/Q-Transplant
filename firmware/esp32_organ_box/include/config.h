#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "Aravindh_Hotspot"
#define WIFI_PASS "Qtransplant123"
#define BACKEND_HOST "http://10.155.109.198:8080"

#define TELEMETRY_ENDPOINT "/api/v1/telemetry/push"
#define EMERGENCY_ENDPOINT "/api/v1/emergency/dispatch"
#define MATCH_ENDPOINT     "/api/v1/matches/"
#define COLD_BOX_ID "BOX-ESP32-001"

#define OLED_SDA_PIN    21
#define OLED_SCL_PIN    22
#define OLED_RESET      -1
#define SCREEN_WIDTH   128
#define SCREEN_HEIGHT   64
#define OLED_I2C_ADDR 0x3C

#define BTN_EMERGENCY   13
#define BTN_DONOR       12
#define BTN_ACKNOWLEGE  14

#define LED_GREEN       18
#define LED_RED         19
#define BUZZER_PIN      23

#define TELEMETRY_INTERVAL_MS 4000
#define TEMP_SAFE_MIN 2.0
#define TEMP_SAFE_MAX 8.0

#endif // CONFIG_H
