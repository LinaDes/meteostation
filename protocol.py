# - *- coding: utf- 8 - *-

import sys
import serial
import time

import math

from slip import SlipConv
import struct


class Protocol:

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
        print ' '.join("%X" % ord(c) if ord(c) > 0x0f else '0' + "%X" % ord(c) for c in packet)

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
        if self.receiveAnswer() == ((chr(0) + chr(0x55) + chr(0xAA) + chr(0x55) + chr(0xAA))):
            if self.log:
                print ('Ping to ' + str(adr) + ' OK')
            return True
        else:
            return False

    def getTemp(self, adr):
        if self.log:
            print ('Get a temperature from sensors.')
        self.sendCommand(chr(adr) + chr(1) + chr(1))
        res = self.receiveAnswer()
        num = ord(res[1])
        values = []
        print 'It has ' + str(num) + ' sensors.'
        for i in range(0, num):
            temp, = struct.unpack('<f', res[i*12+2:i*12+6])
            sernum = res[i*12+6:i*12+14]
            values.append((temp, sernum))
            if self.log:
                print ("%.1f" % temp + 'C on the sensor with the serial number'),
                self.printPacket(sernum)
        return values

    def getPressure(self, adr):
        if self.log:
            print ('Get an atmospheric pressure.')
        self.sendCommand(chr(adr) + chr(1) + chr(2))
        res = self.receiveAnswer()
        pressure, = struct.unpack('<i', res[1:5])
        sernum = res[5]
        if self.log:
            print (str(pressure) + ' mmHg on the sensor with the serial number'),
            self.printPacket(sernum)
        return pressure, sernum

    def getHumidity(self, adr):
        if self.log:
            print ('Get a humidity.')
        self.sendCommand(chr(adr) + chr(1) + chr(3))
        res = self.receiveAnswer()
        humidity, = struct.unpack('<f', res[1:5])
        sernum = res[5]
        if self.log:
            if math.isnan(humidity):
                print 'The humidity sensor doesn\'t exist'
            else:
                print (str(humidity) + '% on the sensor with the serial number'),
                self.printPacket(sernum)
        return humidity, sernum

    def close(self):
        self.ser.close()



