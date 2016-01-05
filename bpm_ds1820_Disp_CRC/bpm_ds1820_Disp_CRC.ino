#include <DallasTemperature.h>
#include <Adafruit_GFX.h>
#include <Adafruit_PCD8544.h>
#include <Adafruit_BMP085.h>
#include <OneWire.h>


#define ONE_WIRE_BUS 10
#define TEMPERATURE_PRECISION 9

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
DeviceAddress insideThermometer, outsideThermometer;
Adafruit_PCD8544 display = Adafruit_PCD8544(3, 4, 5, 6, 7);
Adafruit_BMP085 bmp;

const int bufLength = 8;
const char SLIP_END = '\xC0';
const char SLIP_ESC = '\xDB';
const char SLIP_ESC_END = '\xDC';
const char SLIP_ESC_ESC = '\xDD';

int readCommand(char *buf)
{
  int i = 0;
  bool escaped = false;
  char c = (char) Serial.read();
  if (c == SLIP_END)
  {
    bool beginflag = true;
    while (beginflag)
    {
      char c1 = (char) Serial.read();
      switch (c1)
      {
        case SLIP_END:
          return i;
          break;
        case SLIP_ESC:
          escaped = true;
          break;
        case SLIP_ESC_END:
          if (escaped)
          {
            buf[i] = SLIP_END;
            escaped = false;
          }
          else
            buf[i] = c1;
          break;
        case SLIP_ESC_ESC:
          if (escaped)
          {
            buf[i] = SLIP_ESC;
            escaped = false;
          }
          else
            buf[i] = c1;
          break;
        default:
          if (escaped)
          {
            return 0;
          }
          else
          buf[i] = c1;
        break;
      }
      i++;
    }
  }
  return i;
}

int transferData(char *buf, unsigned char cnt)
{
  Serial.print(SLIP_END);
  for (int i = 0; i < cnt; i++)
  {
    switch (buf[i])
    {
      case SLIP_END:
        Serial.print(SLIP_ESC);
        Serial.print(SLIP_ESC_END);
        break;
      case SLIP_ESC:
        Serial.print(SLIP_ESC);
        Serial.print(SLIP_ESC_ESC);
        break;
      default:
        Serial.print(buf[i]);
        break;
    }
  }
  Serial.print(SLIP_END);
}

unsigned short getCRC(char *buf, unsigned char cnt)
{
  unsigned temp, temp2, flag;
  temp = 0xFFFF;
  for (int i = 0; i < cnt; i++)
  {
    temp = temp ^ buf[i];
    for (int j = 1; j <= 8; j++)
    { 
      flag = temp & 0x0001;
      temp = temp >> 1;
      if (flag)
        temp = temp ^ 0xA001;
    }
  }
  temp2 = temp >> 8;
  temp = (temp << 8) | temp2;
  temp &= 0xFFFF;
  return temp;
}

int addCRC(char *buf, unsigned char cnt)
{
  unsigned short crc = getCRC(buf, cnt);
  memcpy(&buf[cnt], &crc, 2);
  return cnt + 2;
}


void setup()
{
  Serial.begin(9600);
  bmp.begin();
  display.begin();
  display.clearDisplay();
  display.setContrast(40);
  display.display();
//  pinMode(13, OUTPUT);

  sensors.begin();
  //  Serial.print("Locating devices...");
  //  Serial.print("Found ");
  //  Serial.print(sensors.getDeviceCount(), DEC);
  //  Serial.println(" devices.");
  //  if (!sensors.getAddress(insideThermometer, 0)) Serial.println("Unable to find address for Device 0");
  //  if (!sensors.getAddress(outsideThermometer, 1)) Serial.println("Unable to find address for Device 1");
  sensors.getAddress(insideThermometer, 0);
  sensors.getAddress(outsideThermometer, 1);
  //  Serial.print("Device 0 Address: ");
  //  printAddress(insideThermometer);
  //  Serial.println();
  //  Serial.print("Device 1 Address: ");
  //  printAddress(outsideThermometer);
  //  Serial.println();
  sensors.setResolution(insideThermometer, TEMPERATURE_PRECISION);
  sensors.setResolution(outsideThermometer, TEMPERATURE_PRECISION);
}


void printAddress(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

void loop()
{
  display.clearDisplay();
  display.display();
  char readbuf[100];
  char writebuf[100];
  char tmpbuf[50];
  int msglen = readCommand(readbuf);
  if (msglen)
  {
    unsigned short msgcrc;
    memcpy(&msgcrc, &readbuf[msglen-2], 2);
    unsigned short crc = getCRC(readbuf, msglen-2);
    if (crc == msgcrc)
    {
      sprintf(tmpbuf, "%x", msgcrc);
      for (int i = 0; i < 4; i++)
      {
        display.write(tmpbuf[i]);
      }
      display.write('\n');
      sprintf(tmpbuf, "%x", crc);
      for (int i = 0; i < 4; i++)
      {
        display.write(tmpbuf[i]);
      }
      display.write('\n');
    }
    
  }

  display.display();

//  memcpy(writebuf, readbuf, 4);
  writebuf[0] = '\x01';
  writebuf[1] = '\x02';
  writebuf[2] = '\xC0';
  writebuf[3] = '\x03';

  
  int ccc = addCRC(writebuf, 4);
  
  transferData(writebuf, ccc);
  
  delay(4000);
  display.clearDisplay();
  sensors.requestTemperatures();

  display.clearDisplay();
  display.display();

  float temp1 = sensors.getTempC(insideThermometer);
  float temp2 = sensors.getTempC(outsideThermometer);

  char buf[bufLength];
  display.setCursor(0, 0);
  display.setTextColor(BLACK);
  display.setTextSize(1);
  float temperature = bmp.readTemperature();
  int32_t pressure = (int32_t)(bmp.readPressure() / 133.3224);

//  display.write(END);
  display.write('T');
  display.write('-');
  memset(buf, 0, sizeof(buf));
  dtostrf(temperature, 4, 2, buf);
  for (int i = 0; i < bufLength; i++)
  {
  display.write(buf[i]);
  }
  display.write('\n');

  display.write('T');
  display.write('1');
  display.write('-');
  memset(buf, 0, sizeof(buf));
  dtostrf(temp1, 4, 2, buf);
  for (int i = 0; i < bufLength; i++)
  {
  display.write(buf[i]);
  }
  display.write('\n');

  display.write('T');
  display.write('2');
  display.write('-');
  memset(buf, 0, sizeof(buf));
  dtostrf(temp2, 4, 2, buf);
  for (int i = 0; i < bufLength; i++)
  {
  display.write(buf[i]);
  }
  display.write('\n');


  //  display.setCursor(0, LCDHEIGHT/2);
  display.write('P');
  display.write('-');
  memset(buf, 0, sizeof(buf));
  sprintf(buf, "%ld", pressure);
  for (int i = 0; i < bufLength; i++)
  {
  display.write(buf[i]);
  }


  display.display();
  delay(2000);

  }

