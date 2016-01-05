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
    printPacket(out)
    ser.write(out)
    print ('Sent ' + str(len(out)) + ' bytes: '),
    printPacket(out)

def receiveAnswer():
    result = ''
    char = ser.read(1)
    if char == SLIP_END:
        result += char
        beginflag = True
        while beginflag:
            c = ser.read(1)
            result += c
            if c == SLIP_END:
                beginflag = False
    print ('Received ' + str(len(result)) + ' bytes: '),
    printPacket(result)
    return result

def makePacket(adr, cs, mtd, data):
    return chr(adr) + chr(cs) + chr(mtd) + chr(data)

# packet = '\x55' + '\xAA' + '\x55' + '\xc0' + '\xAA' + '\x01' + '\x00' + '\x99' + '\x89' + '\x74' + '\xFF' + '\xFC' + '\xC0' + '\x6D'
# packet = '\x00'
# packet = 'a' + 'b' + 'c' + 'd'

packet = makePacket(0, 0x01, 0x01, 0)
print('msg - '),
printPacket(packet)
sendCommand(packet)
packet2 = receiveAnswer()
packet3 = slipC.unslip(packet2)
print ('after antiSLIP - '),
printPacket(packet3)
if slipC.checkcrc(packet3):
    print ('msg - '),
    printPacket(slipC.getmsgpart(packet3))


