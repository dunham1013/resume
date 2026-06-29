#define BLYNK_TEMPLATE_ID "TMPL6HZ3MNqDN"
#define BLYNK_TEMPLATE_NAME "project"
#define BLYNK_AUTH_TOKEN "vASXQ_ipUQU8Ub6vrMwTNeoXTTFGbVUG"

#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <BlynkSimpleStream.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

#define DHTPIN A1
#define DHTTYPE DHT11
#define PUMP_PIN 4
#define FAN_PIN 5
#define HEATER_PIN 6
#define PESTICIDE_PIN 7

char auth[] = BLYNK_AUTH_TOKEN;
DHT dht(DHTPIN, DHTTYPE);
BlynkTimer timer;

int targetSoilMin = 40;  
int targetSoilMax = 60;  
float targetTempMin = 18.0;
float targetTempMax = 28.0;

bool isAutoMode = false;
bool pumpAlertSent = false;
bool fanAlertSent = false;
bool heaterAlertSent = false;
bool pesticideAlertSent = false;

int pesticideStatus = 0;


BLYNK_WRITE(V20) {
  isAutoMode = (param.asInt() == 1);

  if (!isAutoMode) {
    digitalWrite(PUMP_PIN, LOW);
    digitalWrite(FAN_PIN, LOW);
    digitalWrite(HEATER_PIN, LOW);
    digitalWrite(PESTICIDE_PIN, LOW);
    pumpAlertSent = false;
    fanAlertSent = false;
    heaterAlertSent = false;
    pesticideAlertSent = false;
    pesticideStatus = 0;
  }
}

BLYNK_WRITE(V2) { if(!isAutoMode) digitalWrite(PUMP_PIN, param.asInt() == 1 ? HIGH : LOW); }
BLYNK_WRITE(V3) { if(!isAutoMode) digitalWrite(FAN_PIN, param.asInt() == 1 ? HIGH : LOW); }
BLYNK_WRITE(V4) { if(!isAutoMode) digitalWrite(HEATER_PIN, param.asInt() == 1 ? HIGH : LOW); }

BLYNK_WRITE(V6) {
  pesticideStatus = param.asInt();

  if (pesticideStatus == 1) {
    digitalWrite(PESTICIDE_PIN, HIGH);
    
    if (isAutoMode && !pesticideAlertSent) {
      Blynk.logEvent("pesticide_alert", "병충해 감지 농약펌프 가동");
      pesticideAlertSent = true;
    }
    
    delay(1000); 

    digitalWrite(PESTICIDE_PIN, LOW);  
    pesticideStatus = 0;               
    pesticideAlertSent = false;        
    Blynk.virtualWrite(V6, 0);         
    }
  }

BLYNK_WRITE(V10) { targetSoilMin = param.asInt(); }  
BLYNK_WRITE(V11) { targetSoilMax = param.asInt(); }  
BLYNK_WRITE(V12) { targetTempMin = param.asFloat(); }
BLYNK_WRITE(V13) { targetTempMax = param.asFloat(); }

void sendSensorData() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float Soil_moisture = analogRead(A2);
  int soilPercent = map(Soil_moisture, 1023, 0, 0, 100);

  if (!isnan(h) && !isnan(t)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:" + String(t, 1) + "C  H:" + String(h, 0) + "%");
    lcd.setCursor(0, 1);
    lcd.print("Soil Moist:" + String(soilPercent) + "%");
    
    Blynk.virtualWrite(V0, t);          
    Blynk.virtualWrite(V1, soilPercent);
    Blynk.virtualWrite(V5, h);          

    if (isAutoMode) {
      
      if (soilPercent < targetSoilMin) {
        digitalWrite(PUMP_PIN, HIGH);
        if (!pumpAlertSent) {
          Blynk.logEvent("water_alert", "토양 수분 부족 물펌프 가동");
          pumpAlertSent = true;
        }
      }
      else if (soilPercent >= targetSoilMax) {
        digitalWrite(PUMP_PIN, LOW);  
        pumpAlertSent = false;        
      }

      if (t < targetTempMin) {
        digitalWrite(HEATER_PIN, HIGH);
        digitalWrite(FAN_PIN, LOW);    
        fanAlertSent = false;          
        if (!heaterAlertSent) {
          Blynk.logEvent("heater_alert", "온도 낮음 가열히터 가동");
          heaterAlertSent = true;
        }
      }
      else if (t > targetTempMax) {
        digitalWrite(HEATER_PIN, LOW);
        digitalWrite(FAN_PIN, HIGH);    
        heaterAlertSent = false;        
        if (!fanAlertSent) {
          Blynk.logEvent("fan_alert", "온도 높음 쿨링팬 가동");
          fanAlertSent = true;
        }
      }
      else {
        digitalWrite(HEATER_PIN, LOW);
        digitalWrite(FAN_PIN, LOW);
        heaterAlertSent = false;
        fanAlertSent = false;    
      }
    }
  }
}

void setup(){
  Serial.begin(9600);
  
  lcd.init();
  lcd.backlight();
  dht.begin();

  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(HEATER_PIN, OUTPUT);
  pinMode(PESTICIDE_PIN, OUTPUT);
 
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(HEATER_PIN, LOW);
  digitalWrite(PESTICIDE_PIN, LOW);
  
  Blynk.begin(Serial, auth);
  timer.setInterval(3000L, sendSensorData);
}

void loop(){
  Blynk.run();
  timer.run();
}