/*
  Q-TRANSPLANT — Hospital Emergency Device Firmware (ESP32)
  ------------------------------------------------------------
  Hardware:
    - SSD1306 OLED (I2C, 128x32 or 128x64)
    - Buzzer on BUZZER_PIN (active or passive — see tone() calls)
    - EMERGENCY button, DONOR_FOUND button, ACK button (debounced, INPUT_PULLUP)
    - Kept on a permanent USB/data cable to the hospital terminal so requirement
      text typed on the web dashboard streams straight to the OLED in real time.

  Libraries required (Library Manager):
    - Adafruit_GFX, Adafruit_SSD1306
    - WebSockets by Markus Sattler (arduinoWebSockets)
    - ArduinoJson

  This connects to the backend_emergency_ws.py WebSocket endpoint with this
  device's hospital_id and a device token — never ship a build with the token
  hardcoded in a public repo; use a build-time secret or NVS storage instead.
*/

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ---------- CONFIG ----------
const char* WIFI_SSID   = "Aravindh_Hotspot";
const char* WIFI_PASS   = "Qtransplant123";
const char* WS_HOST     = "your-backend-host.example.com";
const uint16_t WS_PORT  = 443;
const char* WS_PATH     = "/api/v1/emergency/ws";
const char* HOSPITAL_ID = "h1";
const char* HOSPITAL_NAME = "Apollo Central";
const char* DEVICE_TOKEN  = "esp32-device-secret-h1"; // matches backend DEVICE_TOKENS

#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define BUZZER_PIN   25
#define BTN_EMERGENCY 26
#define BTN_DONORFOUND 27
#define BTN_ACK       14

Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);
WebSocketsClient webSocket;

String currentStatus = "idle";
String currentRequirement = "";
unsigned long lastBuzz = 0;
bool buzzing = false;
unsigned long lastDebounce[3] = {0,0,0};
const unsigned long DEBOUNCE_MS = 250;

// ---------- SOUND PATTERNS ----------
void soundAmbulance() {
  // wail: sweep low->high->low, called repeatedly while status == emergency
  for (int f = 500; f <= 1000; f += 40) { tone(BUZZER_PIN, f); delay(8); }
  for (int f = 1000; f >= 500; f -= 40) { tone(BUZZER_PIN, f); delay(8); }
  noTone(BUZZER_PIN);
}

void soundDonorFoundChime() {
  int notes[] = {523, 659, 784, 1047};
  for (int i = 0; i < 4; i++) { tone(BUZZER_PIN, notes[i], 150); delay(160); }
  noTone(BUZZER_PIN);
}

void soundAcknowledgeOff() {
  tone(BUZZER_PIN, 340, 300);
  delay(320);
  noTone(BUZZER_PIN);
}

// ---------- OLED ----------
void renderOled() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(HOSPITAL_NAME);
  display.print("STATUS: ");
  display.println(currentStatus);
  display.println("--------------------");
  display.print("REQ: ");
  display.println(currentRequirement.length() ? currentRequirement : "-- waiting --");
  display.display();
}

// ---------- WEBSOCKET ----------
void sendEvent(const char* type, const char* requirement = nullptr, const char* target = nullptr) {
  StaticJsonDocument<256> doc;
  doc["type"] = type;
  doc["hospital_id"] = HOSPITAL_ID;
  doc["hospital_name"] = HOSPITAL_NAME;
  if (requirement) doc["requirement"] = requirement;
  if (target) doc["target_hospital_id"] = target;
  String out;
  serializeJson(doc, out);
  webSocket.sendTXT(out);
}

void onWsEvent(WStype_t type, uint8_t* payload, size_t length) {
  if (type != WStype_TEXT) return;
  StaticJsonDocument<2048> doc;
  if (deserializeJson(doc, payload, length)) return;
  if (String((const char*)doc["type"]) != "state") return;

  JsonObject me = doc["hospitals"][HOSPITAL_ID];
  if (!me.isNull()) {
    currentStatus = me["status"].as<String>();
    currentRequirement = me["requirement"].as<String>();
  }

  // if ANY hospital besides us is in emergency, buzz like the web dashboard does
  bool anyoneElseEmergency = false;
  for (JsonPair kv : doc["hospitals"].as<JsonObject>()) {
    if (String(kv.key().c_str()) != HOSPITAL_ID &&
        String(kv.value()["status"].as<const char*>()) == "emergency") {
      anyoneElseEmergency = true;
    }
  }
  buzzing = anyoneElseEmergency || currentStatus == "emergency";
  renderOled();
}

// ---------- SETUP / LOOP ----------
void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BTN_EMERGENCY, INPUT_PULLUP);
  pinMode(BTN_DONORFOUND, INPUT_PULLUP);
  pinMode(BTN_ACK, INPUT_PULLUP);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("Connecting WiFi...");
  display.display();

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(300); }

  String path = String(WS_PATH) + "?hospital_id=" + HOSPITAL_ID + "&device_token=" + DEVICE_TOKEN;
  webSocket.beginSSL(WS_HOST, WS_PORT, path.c_str());
  webSocket.onEvent(onWsEvent);
  webSocket.setReconnectInterval(3000);

  renderOled();
}

void loop() {
  webSocket.loop();

  unsigned long t = millis();

  if (digitalRead(BTN_EMERGENCY) == LOW && t - lastDebounce[0] > DEBOUNCE_MS) {
    lastDebounce[0] = t;
    sendEvent("emergency", currentRequirement.c_str());
  }
  if (digitalRead(BTN_DONORFOUND) == LOW && t - lastDebounce[1] > DEBOUNCE_MS) {
    lastDebounce[1] = t;
    sendEvent("donor_found"); // in production, prompt/select which hospital this responds to
    soundDonorFoundChime();
  }
  if (digitalRead(BTN_ACK) == LOW && t - lastDebounce[2] > DEBOUNCE_MS) {
    lastDebounce[2] = t;
    sendEvent("acknowledge");
    soundAcknowledgeOff();
  }

  if (buzzing && t - lastBuzz > 900) {
    lastBuzz = t;
    soundAmbulance();
  }
}
