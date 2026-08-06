/**
 * Q-Transplant ESP32 DevKit Organ Transport Node Firmware
 * Multi-Button Control + SSD1306 OLED + Telemetry + Emergency Siren
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "config.h"

// OLED Display Instance
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// State Variables
unsigned long lastTelemetryTime = 0;
bool isEmergencyState = false;
bool isDonorReady = false;
float simulatedTemp = 4.2;
float simulatedHumidity = 84.0;
float batteryLevel = 98.0;

void updateOLED(const String& statusLine, const String& infoLine = "");

void connectWiFi() {
  Serial.printf("[WIFI] Connecting to %s...\n", WIFI_SSID);
  updateOLED("CONNECTING WIFI", WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) { // 15s timeout
    delay(500);
    Serial.print(".");
    retries++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected! IP: " + WiFi.localIP().toString());
    updateOLED("WIFI CONNECTED", WiFi.localIP().toString());
    digitalWrite(LED_GREEN, HIGH);
  } else {
    Serial.println("\n[WIFI] Connection failed. Running in Offline Mode.");
    updateOLED("WIFI OFFLINE", "Check 2.4GHz/Pass");
  }
  delay(1000);
}

void updateOLED(const String& statusLine, const String& infoLine) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Header Bar
  display.setCursor(0, 0);
  display.println("=== Q-TRANSPLANT ===");
  display.setCursor(0, 10);
  display.printf("BOX: %s\n", COLD_BOX_ID);
  display.drawLine(0, 20, 128, 20, SSD1306_WHITE);

  // Temperature & Battery
  display.setCursor(0, 24);
  display.printf("Temp: %.1f C  Hum: %.0f%%\n", simulatedTemp, simulatedHumidity);
  display.setCursor(0, 34);
  display.printf("Bat : %.0f%%   WiFi: %s\n", batteryLevel, WiFi.status() == WL_CONNECTED ? "OK" : "ERR");

  // Status Line
  display.setCursor(0, 46);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE); // Inverted text for emphasis
  display.println(statusLine);
  display.setTextColor(SSD1306_WHITE);
  
  if (infoLine.length() > 0) {
    display.setCursor(0, 56);
    display.println(infoLine);
  }
  
  display.display();
}

bool sendHttpPost(const String& path, const String& jsonPayload) {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String fullUrl = String(BACKEND_HOST) + path;
  http.begin(fullUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  int httpCode = http.POST(jsonPayload);
  Serial.printf("[HTTP] POST %s -> Response Code: %d\n", path.c_str(), httpCode);
  http.end();
  return (httpCode == 200 || httpCode == 201);
}

void sendTelemetry() {
  StaticJsonDocument<256> doc;
  doc["cold_box_id"] = COLD_BOX_ID;
  doc["lat"] = 12.8945 + ((random(-100, 100)) / 10000.0);
  doc["lng"] = 77.5989 + ((random(-100, 100)) / 10000.0);
  doc["temp_celsius"] = simulatedTemp;
  doc["humidity_percent"] = simulatedHumidity;
  doc["battery_level"] = batteryLevel;

  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  bool success = sendHttpPost(TELEMETRY_ENDPOINT, jsonPayload);
  if (success) {
    digitalWrite(LED_GREEN, HIGH);
  }
}

void triggerEmergency() {
  isEmergencyState = true;
  Serial.println(" [EMERGENCY] SOS Button Pressed!");
  updateOLED("!!! SOS ALERT !!!", "Backend Notified");

  StaticJsonDocument<256> doc;
  doc["cold_box_id"] = COLD_BOX_ID;
  doc["hospital_name"] = "Apollo Specialty Hospital";
  doc["patient_name"] = "CRITICAL TRANSPORT PATIENT";
  doc["organ_type"] = "Heart";
  doc["urgency_level"] = "CRITICAL";

  String payload;
  serializeJson(doc, payload);
  sendHttpPost(EMERGENCY_ENDPOINT, payload);

  // Alarm Pattern: Beep & Red Flash
  for (int i = 0; i < 6; i++) {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(150);
    digitalWrite(LED_RED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

void triggerDonorAvailable() {
  isDonorReady = true;
  Serial.println(" [DONOR] Donor Organ Ready Button Pressed!");
  updateOLED("DONOR ORGAN READY", "Heart (O+) Signal");

  StaticJsonDocument<256> doc;
  doc["donor_id"] = 1;
  doc["organ_type"] = "Heart";
  doc["blood_type"] = "O+";
  doc["hla_type"] = "A2,B7,DR4";
  doc["max_ischemia_hours"] = 4.0;
  doc["cold_box_id"] = COLD_BOX_ID;
  doc["status"] = "available";

  String payload;
  serializeJson(doc, payload);
  sendHttpPost("/api/v1/organs/", payload);

  // Double chime on buzzer
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH); delay(80); digitalWrite(BUZZER_PIN, LOW); delay(80);
  digitalWrite(BUZZER_PIN, HIGH); delay(120); digitalWrite(BUZZER_PIN, LOW);
}

void acknowledgeAlert() {
  Serial.println(" [ACK] Alert Acknowledged by Crew.");
  isEmergencyState = false;
  isDonorReady = false;
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_GREEN, HIGH);
  updateOLED("SYSTEM NORMAL", "Cold-Box Sealed");

  // Soft confirmation beep
  digitalWrite(BUZZER_PIN, HIGH); delay(50); digitalWrite(BUZZER_PIN, LOW);
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n[START] Q-Transplant ESP32 Cold-Box Controller Starting...");

  // Initialize Pin Modes
  pinMode(BTN_EMERGENCY, INPUT_PULLUP);
  pinMode(BTN_DONOR, INPUT_PULLUP);
  pinMode(BTN_ACKNOWLEGE, INPUT_PULLUP);

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize I2C for SSD1306 OLED
  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("[ERROR] SSD1306 OLED Display allocation failed!");
  } else {
    display.clearDisplay();
    updateOLED("SYSTEM INITIALIZING", "Connecting Wi-Fi");
  }

  // Connect to Wi-Fi
  connectWiFi();
  updateOLED("SYSTEM READY", "Box Sealed OK");
}

void loop() {
  // 1. Check Button Inputs (INPUT_PULLUP: Pressed = LOW)
  if (digitalRead(BTN_EMERGENCY) == LOW) {
    delay(50); // Debounce
    if (digitalRead(BTN_EMERGENCY) == LOW) {
      triggerEmergency();
      while(digitalRead(BTN_EMERGENCY) == LOW); // Wait release
    }
  }

  if (digitalRead(BTN_DONOR) == LOW) {
    delay(50);
    if (digitalRead(BTN_DONOR) == LOW) {
      triggerDonorAvailable();
      while(digitalRead(BTN_DONOR) == LOW);
    }
  }

  if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
    delay(50);
    if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
      acknowledgeAlert();
      while(digitalRead(BTN_ACKNOWLEGE) == LOW);
    }
  }

  // 2. Periodic Telemetry Push
  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = millis();
    
    // Simulate minor ambient fluctuations
    simulatedTemp = 4.0 + (random(-3, 4) / 10.0);
    simulatedHumidity = 84.0 + (random(-5, 5) / 10.0);
    batteryLevel = max(10.0f, batteryLevel - 0.005f);

    sendTelemetry();

    if (!isEmergencyState && !isDonorReady) {
      updateOLED("BOX: IN TRANSIT", "Temp: Safe (4.2C)");
    }
  }
}
