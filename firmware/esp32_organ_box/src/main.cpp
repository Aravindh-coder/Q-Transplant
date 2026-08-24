/**
 * Q-Transplant ESP32 DevKit Organ Transport Node Firmware
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "config.h"

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

unsigned long lastTelemetryTime = 0;
bool isEmergencyState = false;
bool isDonorReady = false;
float simulatedTemp = 4.2;
float simulatedHumidity = 84.0;
float batteryLevel = 98.0;

void updateOLED(const String& statusLine, const String& infoLine = "");

// ==============================================================================
// SOUND EFFECTS — mirrors the web app's sound.js so the physical box and the
// dashboard "feel" like the same event (ambulance siren / donor chime / happy
// jingle).
//
// ⚠ BUZZER TYPE MATTERS: a PASSIVE buzzer (3-legged, no black epoxy dome) will
// reproduce the real pitch-sweeping wail via tone(). An ACTIVE buzzer (has a
// small black dome, fixed single pitch) will still play the correct on/off
// RHYTHM but won't sweep pitch — swap to a passive buzzer for the true wail.
// ==============================================================================

/** Real ambulance hi-lo wail — sweeps between two pitches, ~0.85s per cycle. */
void playAmbulanceSiren(int cycles) {
  const int HI = 980;
  const int LO = 620;
  const int STEPS = 12;
  const int STEP_MS = 35;

  for (int c = 0; c < cycles; c++) {
    for (int s = 0; s <= STEPS; s++) {
      int freq = HI - ((HI - LO) * s / STEPS);
      tone(BUZZER_PIN, freq);
      digitalWrite(LED_RED, (s % 2 == 0) ? HIGH : LOW);
      delay(STEP_MS);
    }
    for (int s = 0; s <= STEPS; s++) {
      int freq = LO + ((HI - LO) * s / STEPS);
      tone(BUZZER_PIN, freq);
      digitalWrite(LED_RED, (s % 2 == 0) ? HIGH : LOW);
      delay(STEP_MS);
    }
  }
  noTone(BUZZER_PIN);
  digitalWrite(LED_RED, LOW);
}

/** Donor match found — ~3 second cue: rising arpeggio, double confirm chime,
 *  then a held resolving tone. */
void playDonorFoundSound() {
  int arpeggio[] = {523, 659, 784, 1047}; // C5 E5 G5 C6
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, arpeggio[i], 150);
    delay(90);
  }
  delay(150);

  tone(BUZZER_PIN, 1047, 150); delay(130);
  tone(BUZZER_PIN, 1319, 150); delay(280);
  tone(BUZZER_PIN, 1047, 150); delay(130);
  tone(BUZZER_PIN, 1319, 150); delay(300);

  tone(BUZZER_PIN, 784, 1000); // ~1s sustained resolving tone
  delay(1000);
  noTone(BUZZER_PIN);
}

/** Happy acknowledge jingle — short upbeat run-up, distinct from the donor
 *  found cue. */
void playHappyAckSound() {
  int melody[]    = {784, 1047, 1319, 1568}; // G5 C6 E6 G6
  int durations[] = {130, 130, 130, 350};
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, melody[i], durations[i]);
    delay(durations[i] + 20);
  }
  noTone(BUZZER_PIN);
}

void connectWiFi() {
  Serial.printf("[WIFI] Connecting to %s...\n", WIFI_SSID);
  updateOLED("CONNECTING WIFI", WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) {
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
  
  display.setCursor(0, 0);
  display.println("=== Q-TRANSPLANT ===");
  display.setCursor(0, 10);
  display.printf("BOX: %s\n", COLD_BOX_ID);
  display.drawLine(0, 20, 128, 20, SSD1306_WHITE);

  display.setCursor(0, 24);
  display.printf("Temp: %.1f C  Hum: %.0f%%\n", simulatedTemp, simulatedHumidity);
  display.setCursor(0, 34);
  display.printf("Bat : %.0f%%   WiFi: %s\n", batteryLevel, WiFi.status() == WL_CONNECTED ? "OK" : "ERR");

  display.setCursor(0, 46);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
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

  // Real ambulance hi-lo siren — 4 full wail cycles (~3.4s)
  playAmbulanceSiren(4);
}

void triggerDonorAvailable() {
  isDonorReady = true;
  Serial.println(" [DONOR] Donor Organ Ready Button Pressed!");
  updateOLED("DONOR ORGAN READY", "Heart (O+) Signal");

  StaticJsonDocument<256> doc;
  doc["hospital_name"] = "Fortis Healthcare, Bengaluru";
  doc["organ_type"] = "Heart";
  doc["blood_type"] = "O+";
  doc["hla_type"] = "A2,B7,DR4";
  doc["cold_box_id"] = COLD_BOX_ID;

  String payload;
  serializeJson(doc, payload);
  sendHttpPost("/api/v1/emergency/donor-available", payload);

  digitalWrite(LED_GREEN, HIGH);
  // ~3 second donor-found chime, matching the web dashboard
  playDonorFoundSound();
}

void acknowledgeAlert() {
  Serial.println(" [ACK] Alert Acknowledged by Crew.");
  isEmergencyState = false;
  isDonorReady = false;
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_GREEN, HIGH);
  updateOLED("SYSTEM NORMAL", "Cold-Box Sealed");

  StaticJsonDocument<128> doc;
  doc["cold_box_id"] = COLD_BOX_ID;
  String payload;
  serializeJson(doc, payload);
  sendHttpPost("/api/v1/emergency/acknowledge", payload);

  // Happy resolution jingle, distinct from the donor-found chime
  playHappyAckSound();
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n[START] Q-Transplant ESP32 Cold-Box Controller Starting...");

  pinMode(BTN_EMERGENCY, INPUT_PULLUP);
  pinMode(BTN_DONOR, INPUT_PULLUP);
  pinMode(BTN_ACKNOWLEGE, INPUT_PULLUP);

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("[ERROR] SSD1306 OLED Display allocation failed!");
  } else {
    display.clearDisplay();
    updateOLED("SYSTEM INITIALIZING", "Connecting Wi-Fi");
  }

  connectWiFi();
  updateOLED("SYSTEM READY", "Box Sealed OK");
}

void loop() {
  if (digitalRead(BTN_EMERGENCY) == LOW) {
    delay(50);
    if (digitalRead(BTN_EMERGENCY) == LOW) {
      triggerEmergency();
      while(digitalRead(BTN_EMERGENCY) == LOW);
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

  if (millis() - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = millis();
    
    simulatedTemp = 4.0 + (random(-3, 4) / 10.0);
    simulatedHumidity = 84.0 + (random(-5, 5) / 10.0);
    batteryLevel = max(10.0f, batteryLevel - 0.005f);

    sendTelemetry();

    if (!isEmergencyState && !isDonorReady) {
      updateOLED("BOX: IN TRANSIT", "Temp: Safe (4.2C)");
    }
  }
}
