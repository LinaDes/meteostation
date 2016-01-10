#!/usr/bin/python
__author__ = 'Andrew Kalinin'
from protocol import Protocol
import sys

serialPort = '/dev/ttyUSB0'
baudRate = 9600
if len(sys.argv) == 3:
    serialPort = sys.argv[1]
    baudRate = sys.argv[2]
elif len(sys.argv) == 1:
    print ('Command line: getweather.py serial_port serial_speed')
    print ('Trying with serial_port = ' + serialPort +' and serial_speed = ' + str(baudRate))
else:
    print ('Command line: getweather.py serial_port serial_speed')
    sys.exit(1)

log = False
device = Protocol(serialPort, baudRate, log)
adr = 0
if device.ping(adr):
    pressure = device.getPressure(adr)
    print ('Pressure - ' + str(pressure) + ' mmHg')
    numbers = ord(device.getNumbersOfSensors(adr))
    for i in range(1, numbers+1, 1):
        t, sn = device.getTempFromSensorN(0, i)
        print ('T' + str(i) + ' - ' + "%.1f" % t + ' C, sensor'),
        device.printPacket(sn)
