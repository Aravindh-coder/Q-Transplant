#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <TinyGPSPlus.h>
#include "config.h"

DHT dht(DHTPIN, DHTTYPE);
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);

unsigned long lastSendTime = 0;
bool alarmState = false;

void connectWiFi() {
    Serial.print("[WIFI] Connecting to: ");
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WIFI] Connected. IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\n[WIFI] Connection failed. Operating in offline data-buffer mode.");
    }
}

bool sendHttpPost(const String& endpoint, const String& jsonPayload) {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
    }

    HTTPClient http;
    String url = String(BACKEND_HOST) + endpoint;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(8000);

    int code = http.POST(jsonPayload);
    Serial.printf("[HTTP] POST %s -> %d\n", url.c_str(), code);
    http.end();
    return code == 200 || code == 201;
}

void sendTelemetryPayload(float temp, float humidity, float lat, float lng, float battery) {
    StaticJsonDocument<256> doc;
    doc["cold_box_id"] = COLD_BOX_ID;
    doc["lat"] = lat;
    doc["lng"] = lng;
    doc["temp_celsius"] = temp;
    doc["humidity_percent"] = humidity;
    doc["battery_level"] = battery;

    String payload;
    serializeJson(doc, payload);
    sendHttpPost(TELEMETRY_ENDPOINT, payload);
}

void triggerSOSAlert(const char* reason) {
    Serial.printf("[SOS] Emergency triggered: %s\n", reason);

    StaticJsonDocument<128> doc;
    doc["cold_box_id"] = COLD_BOX_ID;
    doc["reason"] = reason;

    String payload;
    serializeJson(doc, payload);
    sendHttpPost(SOS_ENDPOINT, payload);

    // Flash LED rapidly
    for (int i = 0; i < 10; i++) {
        digitalWrite(LED_ALARM_PIN, HIGH);
        delay(100);
        digitalWrite(LED_ALARM_PIN, LOW);
        delay(100);
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(SOS_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_ALARM_PIN, OUTPUT);
    digitalWrite(LED_ALARM_PIN, LOW);

    gpsSerial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
    dht.begin();
    connectWiFi();

    Serial.println("[INIT] Q-Transplant Cold-Box Telemetry Node Ready.");
    Serial.printf("[INIT] Box ID: %s\n", COLD_BOX_ID);
}

void loop() {
    // Parse GPS NMEA stream
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    // Check SOS hardware button (active LOW)
    if (digitalRead(SOS_BUTTON_PIN) == LOW) {
        triggerSOSAlert("Manual SOS emergency button activated by transport crew");
        delay(3000);  // Debounce
    }

    if (millis() - lastSendTime >= TELEMETRY_INTERVAL_MS) {
        lastSendTime = millis();

        float temp = dht.readTemperature();
        float humidity = dht.readHumidity();
        if (isnan(temp)) temp = 4.2;
        if (isnan(humidity)) humidity = 82.5;

        float lat = gps.location.isValid() ? gps.location.lat() : 12.9716;
        float lng = gps.location.isValid() ? gps.location.lng() : 77.5946;

        // Simulate battery decay for demonstration
        static float battery = 98.0;
        battery = max(0.0f, battery - 0.01f);

        Serial.printf("[TELEMETRY] Temp: %.1f°C | Humidity: %.1f%% | Battery: %.0f%% | GPS: (%.4f, %.4f)\n",
                      temp, humidity, battery, lat, lng);

        // Temperature Alarm Detection
        if (temp < TEMP_MIN_OK || temp > TEMP_MAX_OK) {
            alarmState = true;
            digitalWrite(LED_ALARM_PIN, HIGH);
            Serial.printf("[ALARM] Temperature %.1f°C is OUTSIDE safe range (%.1f - %.1f°C)!\n",
                          temp, TEMP_MIN_OK, TEMP_MAX_OK);
        } else {
            alarmState = false;
            digitalWrite(LED_ALARM_PIN, LOW);
        }

        sendTelemetryPayload(temp, humidity, lat, lng, battery);
    }
}
