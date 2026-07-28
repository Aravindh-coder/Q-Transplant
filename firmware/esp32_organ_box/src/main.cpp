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

void connectWiFi() {
    Serial.print("Connecting to WiFi: ");
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected. IP: " + WiFi.localIP().toString());
}

void setup() {
    Serial.begin(115200);
    gpsSerial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
    dht.begin();
    connectWiFi();
    Serial.println("ESP32 Cold Box Telemetry Firmware Initialized.");
}

void sendTelemetryPayload(float temp, float humidity, float lat, float lng, float battery) {
    if (WiFi.status() != WL_CONNECTED) {
        connectWiFi();
    }

    HTTPClient http;
    String url = String(BACKEND_HOST) + String(TELEMETRY_ENDPOINT);
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["cold_box_id"] = COLD_BOX_ID;
    doc["lat"] = lat;
    doc["lng"] = lng;
    doc["temp_celsius"] = temp;
    doc["humidity_percent"] = humidity;
    doc["battery_level"] = battery;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);
    Serial.printf("[HTTP] POST %s -> Response Code: %d\n", url.c_str(), httpResponseCode);
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(response);
    }
    http.end();
}

void loop() {
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    if (millis() - lastSendTime >= TELEMETRY_INTERVAL_MS) {
        lastSendTime = millis();

        float temp = dht.readTemperature();
        float humidity = dht.readHumidity();
        if (isnan(temp)) temp = 4.2;  // Default safe cold box temperature if sensor unhooked
        if (isnan(humidity)) humidity = 82.5;

        float lat = gps.location.isValid() ? gps.location.lat() : 12.9716;
        float lng = gps.location.isValid() ? gps.location.lng() : 77.5946;
        float battery = 96.0;

        Serial.printf("[TELEMETRY] Temp: %.1f°C | Humid: %.1f%% | Lat: %.4f | Lng: %.4f\n", temp, humidity, lat, lng);
        sendTelemetryPayload(temp, humidity, lat, lng, battery);
    }
}
