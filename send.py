__author__ = 'Andrew Kalinin'

import sys
import serial
import time
from slip import SlipConv


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
        return ''


def ping(adr):
    print ('Ping adr=' + str(adr))
    sendCommand(chr(0) + chr(0) + chr(200) + chr(233) + chr(193))
    # sendCommand(chr(0) + chr(0x55) + chr(0xAA) + chr(0x51) + chr(0xAB) + chr(0xFF))
    if receiveAnswer() == ((chr(0) + chr(0x55) + chr(0xAA) + chr(0x55) + chr(0xAA))):
        print ('Ping to ' + str(adr) + ' OK')
        return True
    else:
        return False

print (ping(0))

# 0xc3 0x69
