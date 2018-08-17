// rf95_reliable_datagram_server.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable messaging server
// with the RHReliableDatagram class, using the RH_RF95 driver to control a RF95 radio.
// It is designed to work with the other example rf95_reliable_datagram_client
// Tested with Anarduino MiniWirelessLoRa, Rocket Scream Mini Ultra Pro with the RFM95W 
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <SPI.h>
//#define CLIENT_ADDRESS 6
#define SERVER_ADDRESS 0
#define RF95_FREQ 868.0

// Singleton instance of the radio driver
RH_RF95 driver;
//RH_RF95 driver(5, 2); // Rocket Scream Mini Ultra Pro with the RFM95W
// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, SERVER_ADDRESS);
// Need this on Arduino Zero with SerialUSB port (eg RocketScream Mini Ultra Pro)
//#define Serial SerialUSB
void setup() 
{
  // Rocket Scream Mini Ultra Pro with the RFM95W only:
  // Ensure serial flash is not interfering with radio communication on SPI bus
//  pinMode(4, OUTPUT);
//  digitalWrite(4, HIGH);
  Serial.begin(115200);
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
}
int nnodes = 11;
unsigned long packetnum = 0;  // packet counter, we increment per xmission
//uint8_t slaves[12] = {11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}; // Array of all client adresses of the arduinos
uint8_t slaves[13] = { 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}; // Array of all client adresses of the arduinos
uint8_t broadcast[] = "Measurement Request";
uint8_t datarequest[] = "Data Request";
// Dont put this on the stack:
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
void loop()
{
    uint8_t len = sizeof(buf);
    uint8_t from;
    delay(100);
    for (int i = 0; i < nnodes; i++)
    {
      from = slaves[i];      
      manager.sendtoWait(datarequest, sizeof(datarequest), from);
      //if (manager.sendtoWait(datarequest, sizeof(datarequest), from))
        //{
      Serial.println((char*)datarequest);
        //}
      if (manager.recvfromAckTimeout(buf, &len, 1000, &from))
      {
        //Serial.print("got reply from : slave");
        //Serial.print(": ");
        Serial.print((char*)buf);
        Serial.print(from, DEC);
        Serial.println(packetnum);
      }
      delay(50);
    }
    packetnum++;
}q

