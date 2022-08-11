#include <LoRa.h>
#include <RTCZero.h>

int counter = 0;

void setup() {
  if (!LoRa.begin(868E6)) {
    while (1);
  }
}

void loop() {
  // send packet
  LoRa.beginPacket();
  LoRa.print("hello ");
  LoRa.print(counter);
  LoRa.endPacket();

  counter++;

  delay(5000);
}
