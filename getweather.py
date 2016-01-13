#!/usr/bin/python
# - *- coding: utf- 8 - *-
__author__ = 'Andrew Kalinin'
from protocol import Protocol
import sys
import sqlite3

serialPort = '/dev/ttyUSB0'
baudRate = 9600
termSensor = 'Датчик температуры'
pressureSensor = 'Датчик давления'

if len(sys.argv) == 3:
    serialPort = sys.argv[1]
    baudRate = sys.argv[2]
elif len(sys.argv) == 1:
    print ('Command line: getweather.py serial_port serial_speed')
    print ('Trying with serial_port = ' + serialPort + ' and serial_speed = ' + str(baudRate))
else:
    print ('Command line: getweather.py serial_port serial_speed')
    sys.exit(1)

dbconnect = sqlite3.connect('test.db')
dbconnect.text_factory = str
cursor = dbconnect.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS sensortypes' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'type TEXT NOT NULL)')
cursor.execute('SELECT type FROM sensortypes')
if len(cursor.fetchall()) == 0:
    cursor.execute('insert into sensortypes (type) values (?)', (termSensor,))
    cursor.execute('insert into sensortypes (type) values (?)', (pressureSensor,))
cursor.execute('CREATE TABLE IF NOT EXISTS sensors' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'type INTEGER NOT NULL,' +
               'sernum TEXT,' +
               'description TEXT NOT NULL,' +
               'place TEXT NOT NULL,' +
               'FOREIGN KEY (type) REFERENCES sensortypes(_id))')
cursor.execute('CREATE TABLE IF NOT EXISTS metering' +
               '(_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' +
               'time INTEGER NOT NULL,' +
               'value REAL NOT NULL,' +
               'sensorid INTEGER NOT NULL,' +
               'FOREIGN KEY (sensorid) REFERENCES sensors(_id))')

log = False
device = Protocol(serialPort, baudRate, log)
adr = 0
if device.ping(adr):
    pressure, sernum = device.getPressure(adr)
    print ('Pressure - ' + str(pressure) + ' mmHg, sensor'),
    device.printPacket(sernum)
    numbers = ord(device.getNumbersOfSensors(adr))
    for i in range(1, numbers+1, 1):
        t, sn = device.getTempFromSensorN(0, i)
        print ('T' + str(i) + ' - ' + "%.1f" % t + ' C, sensor'),
        device.printPacket(sn)
#         cursor.execute('insert into sensortypes (type) values (?)', (sn,))

# dbconnect.commit()
a = cursor.execute('select * from sensortypes')
for row in a:
    print (row[1])
    print ' '.join(hex(ord(c)) for c in row[1])


