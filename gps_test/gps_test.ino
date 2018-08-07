#include <SoftwareSerial.h>
#include <SPI.h>
#include <RHReliableDatagram.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <TinyGPS.h>

/* This sample code demonstrates the normal use of a TinyGPS object.
   It requires the use of SoftwareSerial, and assumes that you have a
   4800-baud serial GPS device hooked up on pins 4(rx) and 3(tx).
*/

TinyGPS gps;
SoftwareSerial ss(4, 3);
#define LED 13
#define SEALEVELPRESSURE_HPA (1013.25)
#define RF95_FREQ 868.0
#define CLIENT_ADDRESS 21
#define SERVER_ADDRESS 0

Adafruit_BME280 bme; // I2C
unsigned long delayTime;
RH_RF95 driver;


// Change to 434.0 or other frequency, must match RX's freq!


RHReliableDatagram manager(driver, CLIENT_ADDRESS);

void setup()
{
  Serial.begin(115200);
  ss.begin(9600);
  
  Serial.print("Simple TinyGPS library v. "); Serial.println(TinyGPS::library_version());
  Serial.println("by Mikal Hart");
  Serial.println();

  Serial.println("Arduino LoRa TX Test!");
  if (!manager.init())
    Serial.println("init failed");

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  //rf95.setTxPower(23, false);
   if (! bme.begin()) 
   {
        Serial.println("Could not find a valid BME280 sensor, check wiring!");
        while (1);
    }
}

uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
float flat, flon;
int newgpsdata = 0;
void loop()
{
  uint8_t len = sizeof(buf);
  uint8_t from; // Server adress   
  char datapacket[40];   
  bool newData = false;
  unsigned long chars;
  unsigned short sentences, failed;
  

  // For one second we parse GPS data and report some key values

  if (manager.available())
  {
    if (manager.recvfromAckTimeout(buf, &len, 2000, &from))
    { 
      for (unsigned long start = millis(); millis() - start < 1000;)
      {
        while (ss.available())
        {
        char c = ss.read();
        // Serial.write(c); // uncomment this line if you want to see the GPS data flowing
        if (gps.encode(c)) // Did a new valid sentence come in?
          newData = true;
        }
      }   
      if (newData)
      {
        unsigned long age;
        gps.f_get_position(&flat, &flon, &age);
        newgpsdata = 1;
        //Serial.print("LAT=");
        //Serial.print(flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6);
        //Serial.print(" LON=");
        //Serial.print(flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6);
        //Serial.print(" SAT=");
        //Serial.print(gps.satellites() == TinyGPS::GPS_INVALID_SATELLITES ? 0 : gps.satellites());
        // Serial.print(" PREC=");
        //Serial.print(gps.hdop() == TinyGPS::GPS_INVALID_HDOP ? 0 : gps.hdop());
      }
  
        gps.stats(&chars, &sentences, &failed);
        //Serial.print(" CHARS=");
        //Serial.print(chars);
        //Serial.print(" SENTENCES=");
        //Serial.print(sentences);
        //Serial.print(" CSUM ERR=");
        //Serial.println(failed);
      if (chars == 0)
        Serial.println("** No characters received from GPS: check wiring **");
      //delay(500);
      //Serial.println((char*)buf);
      //Serial.print("Got measurement request from ");
      //Serial.println(from, DEC);
      //Serial.println("Measuring now and preparing packet");
      
      itoa(int(bme.readTemperature()*100+27315), datapacket, 10);
      itoa(int(bme.readHumidity()*100+10000), datapacket+5, 10);
      ltoa(long(bme.readPressure()*100+10000000), datapacket+10, 10);
      ltoa(long(flat*1000000), datapacket+18,10);
      ltoa(long(flon*1000000), datapacket+26,10);
      itoa(int(newgpsdata),datapacket+33,10);
      //Serial.println(flat);
      //Serial.println(flon);
      //Serial.println(bme.readTemperature()*100);
      //Serial.println(bme.readHumidity()*100);
      //Serial.println(datapacket);      
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
  newgpsdata = 0;
}
