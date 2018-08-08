#include <SoftwareSerial.h>
#include <Wire.h> 
#include <SPI.h>
#include <TinyGPS.h>
#include <SD.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme; // I2C
long loopcount = 0;
long measurement = 0;
const int buttonPin = 2; 
const int csPin = 10;
TinyGPS gps;
SoftwareSerial ss(4, 3);

File myFile;
void setup() {
  
  Serial.begin(115200);
  ss.begin(9600);
  bool status;
  status = bme.begin(); 
  if (!status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring!");
      while (1);
  }
  //Serial.print("Simple TinyGPS library v. "); Serial.println(TinyGPS::library_version());
  //Serial.println("by Mikal Hart");
  //Serial.println(); 
  pinMode(csPin, OUTPUT);
  SD.begin(csPin);
  myFile = SD.open("test.txt", FILE_WRITE);
  myFile.println("#");
  myFile.println("#count;temp;hum;pres;lat;lon;alt;date;time");
  myFile.close();
  
}

void loop() 
{
  int year;
  byte month, day, hour, minute, second, hundredths;
  unsigned long fix_age;
 

  bool newData = false;
  unsigned long chars;
  unsigned short sentences, failed;
  for (unsigned long start = millis(); millis() - start < 1000;)
  {
    while (ss.available())
    {
      char c = ss.read();
      //Serial.write(c); // uncomment this line if you want to see the GPS data flowing
      if (gps.encode(c)) // Did a new valid sentence come in?
        newData = true;
    }
  }

  if (newData)
  {
    float flat, flon;
    unsigned long age;
    gps.f_get_position(&flat, &flon, &age);
    //Serial.print("LAT=");
    //Serial.print(flat == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flat, 6);
    //Serial.print(" LON=");
    //Serial.print(flon == TinyGPS::GPS_INVALID_F_ANGLE ? 0.0 : flon, 6);
    //Serial.print(" SAT=");
    //Serial.print(gps.satellites() == TinyGPS::GPS_INVALID_SATELLITES ? 0 : gps.satellites());
    //Serial.print(" PREC=");
    //Serial.print(gps.hdop() == TinyGPS::GPS_INVALID_HDOP ? 0 : gps.hdop());
    gps.crack_datetime(&year, &month, &day,
    &hour, &minute, &second, &hundredths, &fix_age);
    myFile = SD.open("test.txt", FILE_WRITE);
    myFile.print(measurement++);
    myFile.print(";");
    myFile.print(bme.readTemperature());
    myFile.print(";");
    myFile.print(bme.readHumidity());
    myFile.print(";");
    myFile.print(bme.readPressure());
    myFile.print(";");
    myFile.print(flon, 6);
    myFile.print(";");
    myFile.print(flat, 6);
    myFile.print(";");
    myFile.print(gps.f_altitude());
    myFile.print(";");
    myFile.print(year);
    myFile.print(".");
    myFile.print(month);
    myFile.print(".");
    myFile.print(day);
    myFile.print(";");
    myFile.print(hour);
    myFile.print(":");
    myFile.print(minute);
    myFile.print(":");
    myFile.print(second);
    myFile.println();
    myFile.close();
  }
  
  //gps.stats(&chars, &sentences, &failed);
  //Serial.print(" CHARS=");
  //Serial.print(chars);
  //Serial.print(" SENTENCES=");
  //Serial.print(sentences);
  //Serial.print(" CSUM ERR=");
  //Serial.println(failed);
  //if (chars == 0)
  //  Serial.println("** No characters received from GPS: check wiring **");
}
