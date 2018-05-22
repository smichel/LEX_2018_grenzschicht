// Arduino9x_RX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (receiver)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example Arduino9x_TX

#include <SPI.h>
#include <Wire.h>

#include <RH_RF95.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme; // I2C

#define RFM95_CS 4
#define RFM95_RST 2
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 868.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
// Blinky on receipt
#define LED 13
static char identifier[3] = "01";
void setup() 
{
  pinMode(LED, OUTPUT);     
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  while (!Serial);
  Serial.begin(9600);
  delay(100);

  Serial.println("Arduino LoRa RX Test!");
  
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  bool status;
  status = bme.begin();  
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
      while (1);
  }
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop()
{
  if (rf95.available())
  {
    // Receive master's call for measurements.   
    uint8_t buf[3];
    uint8_t len = sizeof(buf);
    
    if (rf95.recv(buf, &len))
    {
      digitalWrite(LED, HIGH);
      //RH_RF95::printBuffer("Received: ", buf, len);
      //Serial.print("Got: ");
      Serial.print((char*)buf);
      //Serial.print("RSSI: ");
      //Serial.println(rf95.lastRssi(), DEC);
      
      // Check if the call is for me, if yes, send my data
      if (strcmp((char*)buf,identifier) == 0)
      {
      Serial.println("Sending to rf95_server");
      // Send a message to rf95_server
      int temp = int(bme.readTemperature()*100);
      int hum = int(bme.readHumidity()*100);
      long p = long(bme.readPressure()*100);
  
     // char radiopacket[20] = "Hello World #      ";
      char radiopacket[20];
  
      itoa(temp, radiopacket, 10);
      itoa(hum, radiopacket+4, 10);
      ltoa(p, radiopacket+8, 10);
      itoa(packetnum++,radiopacket+16, 10);
      Serial.print("Sending "); Serial.println(radiopacket);
      //radiopacket[19] = 0;
  
      Serial.println("Sending..."); delay(10);
      rf95.send((uint8_t *)radiopacket, 20);

      //Serial.println("Sent a reply");
      digitalWrite(LED, LOW);
      }
    }
    else
    {
      Serial.println("Receive failed");
    }
  }
  
}

void printValues() {
    Serial.print("Temperature = ");
    Serial.print(bme.readTemperature());
    Serial.println(" *C");

    Serial.print("Pressure = ");
    Serial.print(bme.readPressure() / 100.0F);
    Serial.println(" hPa");

    //Serial.print("Approx. Altitude = ");
    //Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
    //Serial.println(" m");

    Serial.print("Humidity = ");
    Serial.print(bme.readHumidity());
    Serial.println(" %");

    Serial.println();
}
