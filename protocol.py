__author__ = 'Andrew Kalinin'

import sys
import serial
import time
from slip import SlipConv
import struct


class Protocol():

    def __init__(self, port, baudrate, logon):
        self.log = logon
        self.slipC = SlipConv()
        self.SLIP_END = '\xc0'
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        try:
            self.ser.open()
        except serial.SerialException as e:
            print ('Oops! IO Error. Check ' + port + ' at ' + str(baudrate) + '.')
            sys.exit(1)
        if self.log:
            print ('Opened ' + port + ' at ' + str(baudrate) + '.')
        time.sleep(2)

    def printPacket(self, packet):
        print ' '.join(hex(ord(c)) for c in packet)

    def sendCommand(self, packet):
        crcPack = self.slipC.addcrc(packet)
        out = self.slipC.slip(crcPack)
        self.ser.write(out)
        if self.log:
            print ('Sent ' + str(len(out)) + ' bytes: '),
            self.printPacket(out)

    def receiveAnswer(self):
        packet = ''
        char = self.ser.read(1)
        if char == self.SLIP_END:
            packet += char
            beginflag = True
            while beginflag:
                c = self.ser.read(1)
                packet += c
                if c == self.SLIP_END:
                    beginflag = False
        if self.log:
            print ('Received ' + str(len(packet)) + ' bytes: '),
        if self.log:
            self.printPacket(packet)
        unsliped = self.slipC.unslip(packet)
        if self.slipC.checkcrc(unsliped):
            if self.log:
                print ('CRC - OK')
            return self.slipC.getmsgpart(unsliped)
        else:
            if self.log:
                print ('BAD CRC')
            return ''


    def ping(self, adr):
        if self.log:
            print ('Ping adr = ' + str(adr))
        self.sendCommand(chr(adr) + chr(0) + chr(200) + chr(233) + chr(193))
        # sendCommand(chr(0) + chr(0x55) + chr(0xAA) + chr(0x51) + chr(0xAB) + chr(0xFF))
        if self.receiveAnswer() == ((chr(0) + chr(0x55) + chr(0xAA) + chr(0x55) + chr(0xAA))):
            if self.log:
                print ('Ping to ' + str(adr) + ' OK')
            return True
        else:
            return False

    def getNumbersOfSensors(self, adr):
        if self.log:
            print ('Get numbers of temperature sensors.')
        self.sendCommand(chr(adr) + chr(1) + chr(0))
        res = self.receiveAnswer()
        if self.log:
            print ('It has ' + str(ord(res[1])) + ' sensors.')
        return res[1]

    def getTempFromSensorN(self, adr, number):
        if self.log:
            print ('Get a temperature from the sensor ' + str(number) + '.')
        self.sendCommand(chr(adr) + chr(1) + chr(1) + chr(number))
        res = self.receiveAnswer()
        temp, = struct.unpack('<f', res[1:5])
        sernum = res[5:len(res)]
        if self.log:
            print ("%.1f" % temp + 'C on the sensor with the serial number'),
            self.printPacket(sernum)
        return temp, sernum

    def getPressure(self, adr):
        if self.log:
            print ('Get an atmospheric pressure.')
        self.sendCommand(chr(adr) + chr(1) + chr(2))
        res = self.receiveAnswer()
        pressure, = struct.unpack('<i', res[1:5])
        if self.log:
            print (str(pressure) + ' mmHg.')
        return pressure



