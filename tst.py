#!/usr/bin/python
# - *- coding: utf- 8 - *-
import math
from protocol import Protocol

deviceAddress = 0
serialPort = '/dev/ttyUSB0'
baudRate = 9600
logEnabled = True

device = Protocol(serialPort, baudRate, logEnabled)
if device.ping(deviceAddress):
    pressure, sernumP = device.getPressure(deviceAddress)
    print ('Pressure - ' + str(pressure) + ' mmHg')
    humidity, sernumH = device.getHumidity(deviceAddress)
    if not math.isnan(humidity):
        print ('Humidity - ' + str(humidity) + '%')
    numbers = ord(device.getNumbersOfSensors(deviceAddress))
    for i in range(1, numbers+1, 1):
        temperature, sn = device.getTempFromSensorN(0, i)
        print ('T' + str(i) + ' - ' + "%.1f" % temperature + ' C, sensor'),
        device.printPacket(sn)
device.close()
