#include <SoftwareSerial.h>
#include <Wire.h> 
#include <SPI.h>
#include <SD.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme; // I2C
long loopcount = 0;
long measurement = 0;
const int buttonPin = 2; 
const int csPin = 10;

File myFile;
void setup() {
  
  Serial.begin(9600);
  bool status;
  status = bme.begin();  
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
      while (1);
  }
  pinMode(csPin, OUTPUT);
  SD.begin(csPin);
  myFile = SD.open("test.txt", FILE_WRITE);
  myFile.println("#");
  myFile.println("#count;temp;hum;pres");
  myFile.close();
}

void loop() 
{
  if (loopcount%10==0){
  myFile = SD.open("test.txt", FILE_WRITE);
  myFile.print(measurement++);
  myFile.print(";");
  myFile.print(bme.readTemperature());
  myFile.print(";");
  myFile.print(bme.readHumidity());
  myFile.print(";");
  myFile.print(bme.readPressure());
  myFile.print(";");
  myFile.println();
  myFile.close();
  }
  loopcount++; 
  delay(100);
}
