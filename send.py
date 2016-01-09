__author__ = 'Andrew Kalinin'

import sys
import serial
import time
from slip import SlipConv
import struct


# if (len(sys.argv) != 3):
#    print "command line: python udp_slip.py serial_port serial_speed"
#    sys.exit()
# serialPort = sys.argv[1]
# baudRate = sys.argv[2]
serialPort = '/dev/ttyUSB0'
baudRate = 9600

slipC = SlipConv()
SLIP_END = '\xc0'

ser = serial.Serial()
ser.port = serialPort
ser.baudrate = baudRate
try:
    ser.open()
except serial.SerialException as e:
    print ('Oops! IO Error. Check the connection on ' + serialPort + ' at ' + str(baudRate) + '.')
    sys.exit(1)
print ('Connected on ' + serialPort + ' at ' + str(baudRate) + '.')
time.sleep(2)

def printPacket(packet):
    print ' '.join(hex(ord(c)) for c in packet)

def sendCommand(packet):
    crcPack = slipC.addcrc(packet)
    out = slipC.slip(crcPack)
    ser.write(out)
    print ('Sent ' + str(len(out)) + ' bytes: '),
    printPacket(out)

def receiveAnswer():
    packet = ''
    char = ser.read(1)
    if char == SLIP_END:
        packet += char
        beginflag = True
        while beginflag:
            c = ser.read(1)
            packet += c
            if c == SLIP_END:
                beginflag = False
    print ('Received ' + str(len(packet)) + ' bytes: '),
    printPacket(packet)
    unsliped = slipC.unslip(packet)
    if slipC.checkcrc(unsliped):
        print ('CRC - OK')
        return slipC.getmsgpart(unsliped)
    else:
        print ('BAD CRC')
        return ''


def ping(adr):
    print ('Ping adr=' + str(adr))
    sendCommand(chr(adr) + chr(0) + chr(200) + chr(233) + chr(193))
    # sendCommand(chr(0) + chr(0x55) + chr(0xAA) + chr(0x51) + chr(0xAB) + chr(0xFF))
    if receiveAnswer() == ((chr(0) + chr(0x55) + chr(0xAA) + chr(0x55) + chr(0xAA))):
        print ('Ping to ' + str(adr) + ' OK')
        return True
    else:
        return False

def getNumbersOfSensors(adr):
    print ('Get numbers of temperature sensors.')
    sendCommand(chr(adr) + chr(1) + chr(0))
    res = receiveAnswer()
    print ('It has ' + str(ord(res[1])) + ' sensors.')
    return res[1]

def getTempFromSensorN(adr, number):
    print ('Get a temperature from the sensor ' + str(number) + '.')
    sendCommand(chr(adr) + chr(1) + chr(1) + chr(number))
    res = receiveAnswer()
    temp, = struct.unpack('<f', res[1:5])
    sernum = res[5:len(res)]
    print ("%.1f" % temp + 'C on the sensor with the serial number'),
    printPacket(sernum)
    return temp, sernum

def getPressure(adr):
    print ('Get an atmospheric pressure.')
    sendCommand(chr(adr) + chr(1) + chr(2))
    res = receiveAnswer()
    pressure, = struct.unpack('<i', res[1:5])
    print (str(pressure) + ' mmHG.')
    return pressure

adr = 0
if ping(adr):
    pressure = getPressure(adr)
    numbers = ord(getNumbersOfSensors(adr))
    for i in range(1, numbers+1, 1):
        t, sn = getTempFromSensorN(0, i)

