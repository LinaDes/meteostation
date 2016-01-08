#include <DallasTemperature.h>
#include <Adafruit_GFX.h>
#include <Adafruit_PCD8544.h>
#include <Adafruit_BMP085.h>
#include <OneWire.h>


#define ONE_WIRE_BUS 10
#define TEMPERATURE_PRECISION 9

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
//DeviceAddress insideThermometer, outsideThermometer, third;
Adafruit_PCD8544 display = Adafruit_PCD8544(3, 4, 5, 6, 7);
Adafruit_BMP085 bmp;
const unsigned char MAXNUMBERS = 10;
DeviceAddress addresses[MAXNUMBERS];
unsigned char numbers;

const int bufLength = 8;
const char SLIP_END = '\xC0';
const char SLIP_ESC = '\xDB';
const char SLIP_ESC_END = '\xDC';
const char SLIP_ESC_ESC = '\xDD';
const char CS_PING = '\x00';
const char CS_INFO = '\x01';
const char LOC_ADR = '\x00';

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
          i++;
          break;
        case SLIP_ESC_ESC:
          if (escaped)
          {
            buf[i] = SLIP_ESC;
            escaped = false;
          }
          else
            buf[i] = c1;
          i++;
          break;
        default:
          if (escaped)
          {
            return 0;
          }
          else
          buf[i] = c1;
          i++;
          break;
      }
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
  unsigned short temp, temp2, flag;
  temp = 0xFFFF;
  for (int i = 0; i < cnt; i++)
  {
    temp ^= (unsigned char) buf[i];
    for (int j = 1; j <= 8; j++)
    { 
      flag = temp & 0x0001;
      temp >>= 1;
      if (flag)
        temp ^= 0xA001;
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
  sensors.begin();
  numbers = 0;
  for (int i = 0; i < MAXNUMBERS; i++)
  {
    if (!sensors.getAddress(addresses[i], i))
       break;
    numbers++;
  }
  for (unsigned char i = 0; i < numbers; i++)
  {
      sensors.setResolution(addresses[i], TEMPERATURE_PRECISION);
//      printAddress(addresses[i]);
  }
}


void printAddress(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    Serial.print(" ");
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
  Serial.println();
}



void loop()
{
  display.clearDisplay();
  display.display();
  char readbuf[100];
  char writebuf[100];
  char tmpbuf[50];

//writebuf[0] = LOC_ADR;
//writebuf[1] = '\x55';
//writebuf[2] = '\xAA';
//writebuf[3] = '\x51';
//writebuf[4] = '\xAB';
//unsigned short crctest = getCRC(writebuf, 5);
//sprintf(tmpbuf, "%x", crctest);
//for (int i = 0; i < 4; i++)
//{
//  display.write(tmpbuf[i]);
//}
//display.write('\n');
  
  int msglen = readCommand(readbuf);

  sprintf(tmpbuf, "%d", numbers);
  for (int i = 0; i < 2; i++)
  {
    display.write(tmpbuf[i]);
  }
  display.write('\n');

  if (msglen)
  {
    unsigned short msgcrc;
    memcpy(&msgcrc, &readbuf[msglen-2], 2);
    unsigned short crc = getCRC(readbuf, msglen-2);
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

    if (crc == msgcrc)
    {
      char adr = readbuf[0];
      char cs = readbuf[1];
      char mtd = readbuf[2];
      int len;
      if (adr == LOC_ADR)
      {
        switch (cs)
        {
          case CS_PING:
            writebuf[0] = LOC_ADR;
            writebuf[1] = '\x55';
            writebuf[2] = '\xAA';
            writebuf[3] = '\x55';
            writebuf[4] = '\xAA';
            len = addCRC(writebuf, 5);
            delay(100);
            transferData(writebuf, len);
            break;
          case CS_INFO:
            switch (mtd)
            {
               case 0:
                  writebuf[0] = LOC_ADR;
                  writebuf[1] = numbers;
                  len = addCRC(writebuf, 2);
                  delay(100);
                  transferData(writebuf, len);
                  break;
            }
            break;
        }
      }
    }
  }

  display.display();
  
  delay(5000);
  display.clearDisplay();
  sensors.requestTemperatures();

  display.clearDisplay();
  display.display();

  float temp1 = sensors.getTempC(addresses[0]);
  float temp2 = sensors.getTempC(addresses[1]);

  char buf[bufLength];
  display.setCursor(0, 0);
  display.setTextColor(BLACK);
  display.setTextSize(1);
  float temperature = bmp.readTemperature();
  int32_t pressure = (int32_t)(bmp.readPressure() / 133.3224);

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

