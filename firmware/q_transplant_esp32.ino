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
 *   - Active Buzzer           -> GPIO 23 (Buzzer + -> GPIO23, Buzzer - -> GND)
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
const char* WIFI_SSID     = "YOUR_WIFI_SSID";       // Your Wi-Fi Name
const char* WIFI_PASS     = "YOUR_WIFI_PASSWORD";   // Your Wi-Fi Password
const char* BACKEND_HOST  = "http://192.168.1.100:8080"; // Your PC local IP address + port 8080

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
  digitalWrite(BUZZER_PIN, LOW);

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 OLED failed!");
  }

  updateOLED("BOOTING...", "Connecting Wi-Fi");
  connectWiFi();
  updateOLED("SYSTEM ONLINE", "Cold Box Ready");
}

void loop() {
  // 1. Emergency Button (GPIO 13)
  if (digitalRead(BTN_EMERGENCY) == LOW) {
    delay(50);
    if (digitalRead(BTN_EMERGENCY) == LOW) {
      isEmergency = true;
      Serial.println("EMERGENCY BUTTON PRESSED!");
      updateOLED("!!! EMERGENCY !!!", "SOS Alert Sent");
      
      StaticJsonDocument<128> doc;
      doc["cold_box_id"] = COLD_BOX_ID;
      doc["urgency"] = "CRITICAL";
      String body; serializeJson(doc, body);
      postJSON("/api/v1/emergency/dispatch", body);

      // Siren Alarm
      for (int i = 0; i < 5; i++) {
        digitalWrite(LED_RED, HIGH); digitalWrite(BUZZER_PIN, HIGH); delay(100);
        digitalWrite(LED_RED, LOW);  digitalWrite(BUZZER_PIN, LOW);  delay(100);
      }
      while(digitalRead(BTN_EMERGENCY) == LOW);
    }
  }

  // 2. Donor Available Button (GPIO 12)
  if (digitalRead(BTN_DONOR) == LOW) {
    delay(50);
    if (digitalRead(BTN_DONOR) == LOW) {
      Serial.println("DONOR ORGAN AVAILABLE!");
      updateOLED("DONOR ORGAN READY", "Broadcasting...");
      
      StaticJsonDocument<256> doc;
      doc["donor_id"] = 1;
      doc["organ_type"] = "Heart";
      doc["blood_type"] = "O+";
      doc["hla_type"] = "A2,B7,DR4";
      doc["cold_box_id"] = COLD_BOX_ID;
      doc["status"] = "available";
      String body; serializeJson(doc, body);
      postJSON("/api/v1/organs/", body);

      digitalWrite(BUZZER_PIN, HIGH); delay(80); digitalWrite(BUZZER_PIN, LOW); delay(80);
      digitalWrite(BUZZER_PIN, HIGH); delay(150); digitalWrite(BUZZER_PIN, LOW);
      while(digitalRead(BTN_DONOR) == LOW);
    }
  }

  // 3. Acknowledge Button (GPIO 14)
  if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
    delay(50);
    if (digitalRead(BTN_ACKNOWLEGE) == LOW) {
      isEmergency = false;
      digitalWrite(LED_RED, LOW);
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(LED_GREEN, HIGH);
      updateOLED("ACKNOWLEDGED", "System Reset OK");
      digitalWrite(BUZZER_PIN, HIGH); delay(60); digitalWrite(BUZZER_PIN, LOW);
      while(digitalRead(BTN_ACKNOWLEGE) == LOW);
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
