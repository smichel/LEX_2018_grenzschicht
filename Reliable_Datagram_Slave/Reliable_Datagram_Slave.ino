// rf95_reliable_datagram_client.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable messaging client
// with the RHReliableDatagram class, using the RH_RF95 driver to control a RF95 radio.
// It is designed to work with the other example rf95_reliable_datagram_server
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with the RFM95W 
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme; // I2C
#define RF95_FREQ 868.0
#define LED 13
#define CLIENT_ADDRESS 11
#define SERVER_ADDRESS 0
// Singleton instance of the radio driver
RH_RF95 driver;
//RH_RF95 driver(5, 2); // Rocket Scream Mini Ultra Pro with the RFM95W
// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, CLIENT_ADDRESS);
// Need this on Arduino Zero with SerialUSB port (eg RocketScream Mini Ultra Pro)
//#define Serial SerialUSB
void setup() 
{
  // Rocket Scream Mini Ultra Pro with the RFM95W only:
  // Ensure serial flash is not interfering with radio communication on SPI bus
//  pinMode(4, OUTPUT);
//  digitalWrite(4, HIGH);
  pinMode(LED, OUTPUT);     
  Serial.begin(9600);
  while (!Serial) ; // Wait for serial port to be available
  if (!manager.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
    driver.setTxPower(23, false);
    driver.setFrequency(RF95_FREQ);
  // If you are using Modtronix inAir4 or inAir9,or any other module which uses the
  // transmitter RFO pins and not the PA_BOOST pins
  // then you can configure the power transmitter power for -1 to 14 dBm and with useRFO true. 
  // Failure to do that will result in extremely low transmit powers.
//  driver.setTxPower(14, true);
  // You can optionally require this module to wait until Channel Activity
  // Detection shows no activity on the channel before transmitting by setting
  // the CAD timeout to non-zero:
//  driver.setCADTimeout(10000);
  bool status;
  status = bme.begin();  
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
      while (1);
  }
}
//uint8_t data[] = "Hello World!";
// Dont put this on the stack:
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
void loop()
{
  uint8_t len = sizeof(buf);
  uint8_t from; // Server adress   
  char datapacket[20];
  //Serial.println("Sending to rf95_reliable_datagram_server");
  if (manager.available())
  {
    if (manager.recvfromAckTimeout(buf, &len, 2000, &from))
    { 
      //delay(500);
      //Serial.println((char*)buf);
      //Serial.print("Got measurement request from ");
      //Serial.println(from, DEC);
      //Serial.println("Measuring now and preparing packet");
      itoa(int(bme.readTemperature()*100+27315), datapacket, 10);
      itoa(int(bme.readHumidity()*100+10000), datapacket+5, 10);
      ltoa(long(bme.readPressure()*100+10000000), datapacket+10, 10);
      //Serial.println(bme.readTemperature()*100);
      //Serial.println(bme.readHumidity()*100);
      //Serial.println(bme.readPressure()*100);
      //delay(500);
      if (manager.sendtoWait((uint8_t *)datapacket, sizeof(datapacket), from))
      {
      digitalWrite(LED, HIGH);
      //Serial.print("Send ");
      //Serial.println((char*)datapacket);
      //Serial.print("to ");
      //Serial.println(from, HEX);
      digitalWrite(LED, LOW);
      }
    } 

  }
}
