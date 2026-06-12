#include <Servo.h>
#include "WiFiEsp.h"
#include <WiFiEspUdp.h>
#include "SoftwareSerial.h"

#define CLAW_PIN 7
#define ROTATE_PIN 8
#define UP_DOWN_PIN 9
#define FW_BW_PIN 10

SoftwareSerial softserial(4, 5); 

char ssid[] = "MERCUSYS_D2B9";     
char pass[] = "221351518"; 

int status = WL_IDLE_STATUS;     
unsigned int local_port = 8888;  

char packetBuffer[255];          
Servo claw;
Servo updown; 
Servo rotate;
Servo fwbw;
WiFiEspUDP Udp;                  

void setup()
{
  Serial.begin(9600);       
  

  softserial.begin(115200);
  softserial.write("AT+CIOBAUD=9600\r\n");
  softserial.write("AT+RST\r\n");
  delay(1000); 
  softserial.begin(9600);    
  
  Serial.println("\n--- Старт устройства ---");
  WiFi.init(&softserial);    

  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("Ошибка: Модуль не найден!");
    while (true); 
  }

  while (status != WL_CONNECTED) {
    Serial.print("Подключение к SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
  }

  Serial.println("Успешно подключено к Wi-Fi!");
  Serial.print("IP-адрес твоей платы: ");
  Serial.println(WiFi.localIP()); 
  
  Udp.begin(local_port);
  
 
  claw.attach(CLAW_PIN);
  updown.attach(UP_DOWN_PIN);
  rotate.attach(ROTATE_PIN);
  fwbw.attach(FW_BW_PIN);
  Serial.println("Клешня готова. Ожидание UDP команд...\n");
}

void loop()
{
  int packetSize = Udp.parsePacket();
  
  if (packetSize) {
    int len = Udp.read(packetBuffer, 255);
    Udp.flush(); 
    
    if (len > 0) {
      packetBuffer[len] = 0;
    }
    
    Serial.print("[UDP] Получено: ");
    Serial.println(packetBuffer);

  
    if (strcmp(packetBuffer, "F") == 0) {
      Serial.println("Action: ON -> claw.write(170)");
      claw.write(170);
    }

    else if (strcmp(packetBuffer, "G") == 0) {
      Serial.println("Action: OFF -> claw.write(80)");
      claw.write(80);
    }
    memset(packetBuffer, 0, sizeof(packetBuffer));
    Serial.println("------------------------------------");
  }
}
