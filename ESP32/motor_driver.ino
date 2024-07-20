#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <esp_task_wdt.h>

const char *ssid = "Your SSID";
const char *password = "Your Password";
AsyncWebServer server(80);

#define L298N_ENA 14
#define L298N_IN1 25
#define L298N_IN2 26
#define L298N_ENB 12
#define L298N_IN3 17
#define L298N_IN4 13
#define MOTOR_ROUND 0.188
#define FORWARD_RRT 200
#define LR_RRT 230
#define TURN_TIME 1000

void setupPins()
{
  pinMode(L298N_ENA, OUTPUT);
  pinMode(L298N_IN1, OUTPUT);
  pinMode(L298N_IN2, OUTPUT);
  pinMode(L298N_ENB, OUTPUT);
  pinMode(L298N_IN3, OUTPUT);
  pinMode(L298N_IN4, OUTPUT);
}

void stopMotors()
{
  digitalWrite(L298N_ENA, LOW);
  digitalWrite(L298N_IN1, LOW);
  digitalWrite(L298N_IN2, LOW);
  digitalWrite(L298N_ENB, LOW);
  digitalWrite(L298N_IN3, LOW);
  digitalWrite(L298N_IN4, LOW);
}

void moveForward(int duration)
{
  digitalWrite(L298N_IN1, HIGH);
  digitalWrite(L298N_IN2, LOW);
  digitalWrite(L298N_IN3, LOW);
  digitalWrite(L298N_IN4, HIGH);
  analogWrite(L298N_ENA, 255);
  analogWrite(L298N_ENB, 255);
  delay(duration);
  stopMotors();
}

void robotTurnLeft()
{
  analogWrite(L298N_ENA, LR_RRT);
  digitalWrite(L298N_IN1, LOW);
  digitalWrite(L298N_IN2, HIGH);
  analogWrite(L298N_ENB, LR_RRT);
  digitalWrite(L298N_IN3, LOW);
  digitalWrite(L298N_IN4, HIGH);
  delay(TURN_TIME);
  stopMotors();
}

void robotTurnRight()
{
  analogWrite(L298N_ENA, LR_RRT);
  digitalWrite(L298N_IN1, HIGH);
  digitalWrite(L298N_IN2, LOW);
  analogWrite(L298N_ENB, LR_RRT);
  digitalWrite(L298N_IN3, HIGH);
  digitalWrite(L298N_IN4, LOW);
  delay(TURN_TIME);
  stopMotors();
}

void setup()
{
  // Serial.begin(115200);
  setupPins();
  stopMotors();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    // Serial.println("Connecting to WiFi...");
  }
  // Serial.println("Connected to WiFi");
  // Serial.println(WiFi.localIP());

  server.on("/move", HTTP_POST, [](AsyncWebServerRequest *request)
            {
    if (request->hasParam("distance", true) && request->hasParam("direction", true)) {
      int distance = request->getParam("distance", true)->value().toInt();
      String direction = request->getParam("direction", true)->value();
      int duration = distance * 3000;
      xTaskCreatePinnedToCore(
        [](void * params) {
          auto args = *(std::tuple<int, String>*)params;
          moveForward(std::get<0>(args));
          if (std::get<1>(args) == "left") {
            delay(500);
            robotTurnLeft();
          } else if (std::get<1>(args) == "right") {
            delay(500);
            robotTurnRight();
          }
          delete (std::tuple<int, String>*)params;
          vTaskDelete(NULL);
        },
        "MoveTask", 10000, new std::tuple<int, String>(duration, direction), 1, NULL, 0
      );
      request->send(200, "text/plain", "Robot command received");
    } else {
      request->send(400, "text/plain", "Distance or Direction parameter missing");
    } });

  server.begin();
}

void loop()
{
  // 主循环保持空
}
