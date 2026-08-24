/**
 * ==============================================================================
 * Q-TRANSPLANT ESP32 DEVKIT ORGAN COLD-BOX CONTROLLER FIRMWARE (.ino)
 * ==============================================================================
 *
 * HARDWARE CONNECTIONS:
 * ------------------------------------------------------------------------------
 * OLED Display (SSD1306 128x64 I2C):
 *   - VCC  -> 3.3V
 *   - GND  -> GND
 *   - SDA  -> GPIO 21
 *   - SCL  -> GPIO 22
 *
 * Buttons (INPUT_PULLUP: Pin -> Button -> GND):
 *   - Emergency Button        -> GPIO 13
 *   - Donor Available Button  -> GPIO 12
 *   - Acknowledge Button      -> GPIO 14
 *
 * Status Indicators:
 *   - Green Status LED        -> GPIO 18 (with 220 ohm resistor -> GND)
 *   - Red Alert LED           -> GPIO 19 (with 220 ohm resistor -> GND)
 *   - Buzzer                  -> GPIO 23 (Buzzer + -> GPIO23, Buzzer - -> GND)
 *
 * ⚠ BUZZER TYPE MATTERS FOR THE SIREN SOUND:
 *   - PASSIVE buzzer (3-legged, no black epoxy dome, sold as "passive buzzer"):
 *     tone()/noTone() below will drive it and you get a REAL pitch-sweeping
 *     ambulance hi-lo wail — this is what "sound like an ambulance" needs.
 *   - ACTIVE buzzer (has a small black dome, only ever buzzes one fixed pitch):
 *     tone() calls will make no audible pitch difference — you'll still get a
 *     correct on/off RHYTHM (which reads as a siren pattern) but not a real
 *     pitch sweep. If you want the true wail, swap in a passive buzzer.
 * ------------------------------------------------------------------------------
 *
 * ARDUINO LIBRARIES REQUIRED (Install via Arduino Library Manager):
 * 1. Adafruit GFX Library
 * 2. Adafruit SSD1306
 * 3. ArduinoJson (v6.x)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==============================================================================
// CONFIGURATION - UPDATE THESE VALUES FOR YOUR NETWORK
// ==============================================================================
const char* WIFI_SSID     = "Aravindh_Hotspot";       // Your Wi-Fi Name
const char* WIFI_PASS     = "Qtransplant123";         // Your Wi-Fi Password

// ⚠ REQUIRED — replace with YOUR laptop's actual local network IP address.
// Find it by running, on the machine hosting the backend:
//     Linux/Mac:  hostname -I     (or: ip addr show)
//     Windows:    ipconfig        (look for "IPv4 Address")
// The ESP32 and that machine must be on the SAME Wi-Fi network (same SSID
// above), and the backend must be started with --host 0.0.0.0 so it accepts
// connections from other devices on the network, not just localhost, e.g.:
//     uvicorn backend.app.main:app --reload --port 8080 --host 0.0.0.0
// The IP below is a PLACEHOLDER and will NOT work until you change it.
const char* BACKEND_HOST  = "http://192.168.1.100:8080"; // <-- CHANGE THIS

// This device's identity — which hospital this cold-box / control panel
// represents. Must match a hospital name already seeded in the backend
// (see EXTRA_HOSPITALS in backend/app/main.py) so distance/ETA calculations
// resolve correctly.
const char* HOSPITAL_NAME = "Apollo Specialty Hospital";

// For the Donor-Available button demo: which hospital to report as having
// found the donor organ. In a real deployment each hospital runs its own
// device; for a single-device demo this simulates "another hospital found a
// match" so you can see the full DONOR_MATCHED flow end-to-end.
const char* DONOR_HOSPITAL_NAME = "Fortis Healthcare, Bengaluru";

// Box Identification
const char* COLD_BOX_ID   = "BOX-ESP32-001";

// Pin Map
#define OLED_SDA_PIN    21
#define OLED_SCL_PIN    22
#define SCREEN_WIDTH   128
#define SCREEN_HEIGHT   64
#define OLED_RESET      -1

#define BTN_EMERGENCY   13
#define BTN_DONOR       12
#define BTN_ACKNOWLEGE  14

#define LED_GREEN       18
#define LED_RED         19
#define BUZZER_PIN      23

// Timers & Variables
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
unsigned long lastTelemetryMs = 0;
bool isEmergency = false;
float tempVal = 4.2;
float humidityVal = 84.5;
float batVal = 98.0;

// ==============================================================================
// SOUND EFFECTS — mirrors the web app's sound.js so the physical box and the
// dashboard "feel" like the same event (ambulance siren / donor chime / happy
// jingle). Uses tone()/noTone() — see buzzer note above for active vs passive.
// ==============================================================================

/** 🚑 Real ambulance hi-lo wail — sweeps between two pitches, repeated `cycles`
 *  times. Each cycle takes ~0.85s, matching the web siren's cadence. */
void playAmbulanceSiren(int cycles) {
  const int HI = 980;
  const int LO = 620;
  const int STEPS = 12;          // pitch-sweep resolution per half-cycle
  const int STEP_MS = 35;        // ~0.42s per half-sweep -> ~0.84s per full cycle

  for (int c = 0; c < cycles; c++) {
    // Sweep HI -> LO
    for (int s = 0; s <= STEPS; s++) {
      int freq = HI - ((HI - LO) * s / STEPS);
      tone(BUZZER_PIN, freq);
      digitalWrite(LED_RED, (s % 2 == 0) ? HIGH : LOW);
      delay(STEP_MS);
    }
    // Sweep LO -> HI
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

/** 💚 Donor match found — ~3 second cue: rising arpeggio, double confirm
 *  chime, then a held resolving tone. Mirrors playDonorMatchSound() in the
 *  web app. */
void playDonorFoundSound() {
  int arpeggio[] = {523, 659, 784, 1047}; // C5 E5 G5 C6
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, arpeggio[i], 150);
    delay(90);
  }
  delay(150);

  // Two confirmation dings
  tone(BUZZER_PIN, 1047, 150); delay(130);
  tone(BUZZER_PIN, 1319, 150); delay(280);
  tone(BUZZER_PIN, 1047, 150); delay(130);
  tone(BUZZER_PIN, 1319, 150); delay(300);

  // Sustained resolving tone (~1s) to fill out the ~3s total
  tone(BUZZER_PIN, 784, 1000);
  delay(1000);
  noTone(BUZZER_PIN);
}

/** 🎉 Happy acknowledge jingle — short upbeat run-up + resolving chord tone,
 *  distinct from the donor-found cue. Mirrors playHappyAckSound(). */
void playHappyAckSound() {
  int melody[]   = {784, 1047, 1319, 1568}; // G5 C6 E6 G6
  int durations[] = {130, 130, 130, 350};
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, melody[i], durations[i]);
    delay(durations[i] + 20);
  }
  noTone(BUZZER_PIN);
}

void updateOLED(String statusMsg, String subMsg = "") {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.println("=== Q-TRANSPLANT ===");
  display.setCursor(0, 10);
  display.print("BOX: "); display.println(COLD_BOX_ID);
  display.drawLine(0, 20, 128, 20, SSD1306_WHITE);

  display.setCursor(0, 24);
  display.print("Temp: "); display.print(tempVal, 1); display.print("C  Hum: "); display.print(humidityVal, 0); display.println("%");

  display.setCursor(0, 34);
  display.print("Bat : "); display.print(batVal, 0); display.print("%   WiFi: ");
  display.println(WiFi.status() == WL_CONNECTED ? "OK" : "NO");

  display.setCursor(0, 48);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.println(statusMsg);
  display.setTextColor(SSD1306_WHITE);

  if (subMsg.length() > 0) {
    display.setCursor(0, 56);
    display.println(subMsg);
  }
  display.display();
}

void connectWiFi() {
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int count = 0;
  while (WiFi.status() != WL_CONNECTED && count < 15) {
    delay(500);
    Serial.print(".");
    count++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi Connected! IP: " + WiFi.localIP().toString());
    Serial.println("Backend target: " + String(BACKEND_HOST));
    digitalWrite(LED_GREEN, HIGH);
    updateOLED("WIFI CONNECTED", WiFi.localIP().toString());
  } else {
    Serial.println("\nWi-Fi connection failed. Offline Mode.");
    updateOLED("WIFI OFFLINE", "Offline Mode");
  }
}

bool postJSON(String path, String jsonStr) {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String fullUrl = String(BACKEND_HOST) + path;
  http.begin(fullUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(4000);

  int code = http.POST(jsonStr);
  Serial.printf("POST %s -> Code: %d\n", path.c_str(), code);
  if (code <= 0) {
    Serial.println("  -> No response from backend. Check BACKEND_HOST IP, that");
    Serial.println("     the backend is running with --host 0.0.0.0, and that");
    Serial.println("     this ESP32 and the backend machine share the same Wi-Fi.");
  }
  http.end();
  return (code == 200 || code == 201);
}

void sendTelemetry() {
  StaticJsonDocument<256> doc;
  doc["cold_box_id"] = COLD_BOX_ID;
  doc["lat"] = 12.8945;
  doc["lng"] = 77.5989;
  doc["temp_celsius"] = tempVal;
  doc["humidity_percent"] = humidityVal;
  doc["battery_level"] = batVal;

  String body;
  serializeJson(doc, body);
  postJSON("/api/v1/telemetry/push", body);
}

void setup() {
  Serial.begin(115200);

  pinMode(BTN_EMERGENCY, INPUT_PULLUP);
  pinMode(BTN_DONOR, INPUT_PULLUP);
  pinMode(BTN_ACKNOWLEGE, INPUT_PULLUP);

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED, LOW);
  noTone(BUZZER_PIN);

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 OLED failed!");
  }

  updateOLED("BOOTING...", "Connecting Wi-Fi");
  connectWiFi();
  updateOLED("SYSTEM ONLINE", "Cold Box Ready");
}

void loop() {
  // 1. Emergency Button (GPIO 13) — raises the SOS, plays the ambulance siren
  if (digitalRead(BTN_EMERGENCY) == LOW) {
    delay(50);
    if (digitalRead(BTN_EMERGENCY) == LOW) {
      isEmergency = true;
      Serial.println("EMERGENCY BUTTON PRESSED!");
      updateOLED("!!! EMERGENCY !!!", "SOS Alert Sent");

      StaticJsonDocument<256> doc;
      doc["cold_box_id"] = COLD_BOX_ID;
      doc["hospital_name"] = HOSPITAL_NAME;
      doc["organ_type"] = "Heart";
      doc["blood_type"] = "O+";
      doc["hla_type"] = "A2,B7,DR4";
      doc["urgency"] = "CRITICAL";
      String body; serializeJson(doc, body);
      postJSON("/api/v1/emergency/dispatch", body);

      // Real ambulance hi-lo siren — 4 full wail cycles (~3.4s)
      playAmbulanceSiren(4);

      while (digitalRead(BTN_EMERGENCY) == LOW);
    }
  }

  // 2. Donor Available Button (GPIO 12) — broadcasts a donor match AND
  //    registers the organ record. Both calls are needed: the first drives
  //    the live emergency-status card (hospital photo + distance/ETA) on the
  //    dashboard, the second adds the organ to inventory.
  if (digitalRead(BTN_DONOR) == LOW) {
    delay(50);
    if (digitalRead(BTN_DONOR) == LOW) {
      Serial.println("DONOR ORGAN AVAILABLE!");
      updateOLED("DONOR ORGAN READY", "Broadcasting...");

      StaticJsonDocument<256> matchDoc;
      matchDoc["hospital_name"] = DONOR_HOSPITAL_NAME;
      matchDoc["organ_type"] = "Heart";
      matchDoc["blood_type"] = "O+";
      String matchBody; serializeJson(matchDoc, matchBody);
      postJSON("/api/v1/emergency/donor-available", matchBody);

      StaticJsonDocument<256> organDoc;
      organDoc["donor_id"] = 1;
      organDoc["organ_type"] = "Heart";
      organDoc["blood_type"] = "O+";
      organDoc["hla_type"] = "A2,B7,DR4";
      organDoc["cold_box_id"] = COLD_BOX_ID;
      organDoc["status"] = "available";
      String organBody; serializeJson(organDoc, organBody);
      postJSON("/api/v1/organs/", organBody);

      // ~3 second donor-found chime, matching the web dashboard
      playDonorFoundSound();

      while (digitalRead(BTN_DONOR) == LOW);
    }
  }

  // 3. Acknowledge Button (GPIO 14) — resolves the emergency, happy jingle
  if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
    delay(50);
    if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
      isEmergency = false;
      digitalWrite(LED_RED, LOW);
      digitalWrite(LED_GREEN, HIGH);
      updateOLED("ACKNOWLEDGED", "System Reset OK");

      StaticJsonDocument<128> doc;
      doc["cold_box_id"] = COLD_BOX_ID;
      String body; serializeJson(doc, body);
      postJSON("/api/v1/emergency/acknowledge", body);

      playHappyAckSound();

      while (digitalRead(BTN_ACKNOWLEGE) == LOW);
    }
  }

  // 4. Telemetry Cycle (Every 4s)
  if (millis() - lastTelemetryMs >= 4000) {
    lastTelemetryMs = millis();
    tempVal = 4.0 + (random(-2, 3) / 10.0);
    sendTelemetry();
    if (!isEmergency) {
      updateOLED("IN TRANSIT", "Temp Safe (4.2C)");
    }
  }
}
