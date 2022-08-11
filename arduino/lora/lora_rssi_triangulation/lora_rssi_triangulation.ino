#include <SPI.h>
#include <LoRa.h>

int counter = 0;
long id = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Sender");

  if (!LoRa.begin(868E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  randomSeed(analogRead(0));
  id = random(1000000);
  Serial.print("ID initialized as ");
  Serial.println(id);
}

void loop() {
  Serial.print("Sending packet: ");
  Serial.println(counter);

  // send packet
  LoRa.beginPacket();
  LoRa.print(id);
  LoRa.endPacket();

  counter++;

  int packetSize = 0;
  int readCounter = 0;
  
  while(!packetSize && readCounter < 100) {
    readCounter++;
    packetSize = LoRa.parsePacket();
    delay(10);  
  }
  if(packetSize) {
    String data = String("");
    while (LoRa.available()) {
      data += (char)LoRa.read();
    }
    Serial.print("Got ");
    Serial.println(data);
  
    int rssi = LoRa.packetRssi();
    Serial.println(rssi);  
  }
  delay(10 * readCounter);
}
