#!/usr/bin/python
# - *- coding: utf- 8 - *-
import math
from protocol import Protocol
import sys
import time
from dbhelper import DBHelper

deviceAddress = 0
serialPort = '/dev/ttyUSB0'
baudRate = 9600
logEnabled = True

dbFileName = 'weatherstation.db'

termSensorType = 1
pressureSensorType = 2
humiditySensorType = 3

if len(sys.argv) == 3:
    serialPort = sys.argv[1]
    baudRate = sys.argv[2]
    deviceAddress = sys.argv[3]
    logEnabled = sys.argv[4]
elif len(sys.argv) == 1:
    print ('Command line: getweather.py serial_port serial_speed')
    print ('Trying with serial_port = ' + serialPort + ' and serial_speed = ' + str(baudRate))
else:
    print ('Command line: getweather.py serial_port serial_speed')
    sys.exit(1)

currenttime = time.time()
db = DBHelper(dbFileName)

device = Protocol(serialPort, baudRate, logEnabled)
if device.ping(deviceAddress):
    pressure, sernumP = device.getPressure(deviceAddress)
    print ('Pressure - ' + str(pressure) + ' mmHg')
    pressureSensorId = db.getSensorId(pressureSensorType, sernumP)
    db.storeValue(currenttime, pressure, pressureSensorId)
    humidity, sernumH = device.getHumidity(deviceAddress)
    if not math.isnan(humidity):
        print ('Humidity - ' + str(humidity) + '%')
        humiditySensorID = db.getSensorId(humiditySensorType, sernumH)
        db.storeValue(currenttime, humidity, humiditySensorID)
    numbers = ord(device.getNumbersOfSensors(deviceAddress))
    for i in range(1, numbers+1, 1):
        temperature, sn = device.getTempFromSensorN(0, i)
        print ('T' + str(i) + ' - ' + "%.1f" % temperature + ' C, sensor'),
        device.printPacket(sn)
        termSensorId = db.getSensorId(termSensorType, sn)
        db.storeValue(currenttime, temperature, termSensorId)
db.close()
