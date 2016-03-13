#include <DallasTemperature.h>
#include <Adafruit_GFX.h>
#include <Adafruit_PCD8544.h>
#include <Adafruit_BMP085.h>
#include <OneWire.h>
#include <DHT.h>


#define ONE_WIRE_BUS 10
#define TEMPERATURE_PRECISION 9

#define DHTPIN 2
#define DHTTYPE DHT22

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
Adafruit_PCD8544 display = Adafruit_PCD8544(3, 4, 5, 6, 7);
Adafruit_BMP085 bmp;
const unsigned char MAXNUMBERS = 10;
DeviceAddress addresses[MAXNUMBERS];
unsigned char numbers;
DHT dht(DHTPIN, DHTTYPE);

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
  dht.begin();
}

void loop()
{
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
  }

  char readbuf[100];
  char writebuf[130];
  char tmpbuf[50];

  sensors.requestTemperatures();
  int32_t pressure = (int32_t)(bmp.readPressure() / 133.3224);

  float humidity = dht.readHumidity();
  
  int msglen = readCommand(readbuf);
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
      unsigned char n;
      float temp;
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
                case 1:
                  writebuf[0] = LOC_ADR;
                  writebuf[1] = numbers;
                  for (int i=0; i < numbers; i++)
                  {
                    temp = sensors.getTempC(addresses[i]);
                    memcpy(&writebuf[i*12+2], &temp, 4);
                    memcpy(&writebuf[i*12+6], &addresses[i], 8);
                  }
                  len = addCRC(writebuf, numbers*12+2);
                  delay(100);
                  transferData(writebuf, len);
                  break;
                case 2:
                  writebuf[0] = LOC_ADR;
                  memcpy(&writebuf[1], &pressure, 4);
                  writebuf[5] = 0;
                  len = addCRC(writebuf, 6);
                  delay(100);
                  transferData(writebuf, len);
                  break;
                case 3:
                  writebuf[0] = LOC_ADR;
                  memcpy(&writebuf[1], &humidity, 4);
                  writebuf[5] = 0;
                  len = addCRC(writebuf, 6);
                  delay(100);
                  transferData(writebuf, len);
                  break;
                  
            }
            break;
        }
      }
    }
  }

  display.clearDisplay();
  display.display();

  char buf[bufLength];
  display.setCursor(0, 0);
  display.setTextColor(BLACK);
  display.setTextSize(1);

  display.write('P');
  display.write('-');
  memset(buf, 0, sizeof(buf));
  sprintf(buf, "%ld", pressure);
  for (int i = 0; i < bufLength; i++)
  {
    display.write(buf[i]);
  }
  display.write('\n');
  if (!isnan(humidity))
  {
    display.write('H');
    display.write('-');
    memset(buf, 0, sizeof(buf));
    dtostrf(humidity, 4, 2, buf);
    for (int i = 0; i < bufLength; i++)
    {
      display.write(buf[i]);
    }
    display.write('\n');
  }
  char tnum = '1';
  for (int i = 0; i < numbers; i++)
  {
    float temp = sensors.getTempC(addresses[i]);
    display.write('T');
    display.write(tnum);
    display.write('-');
    memset(buf, 0, sizeof(buf));
    dtostrf(temp, 4, 2, buf);
    for (int i = 0; i < bufLength; i++)
    {
      display.write(buf[i]);
    }
    display.write('\n');
    tnum++;
  }
  display.display();
  delay(250);
}

