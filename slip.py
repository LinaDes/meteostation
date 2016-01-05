__author__ = 'Andrew Kalinin'

class SlipConv():

    def __init__(self):
        self.started = False
        self.escaped = False
        self.packet = ''
        self.SLIP_END = '\xc0'
        self.SLIP_ESC = '\xdb'
        self.SLIP_ESC_END = '\xdc'
        self.SLIP_ESC_ESC = '\xdd'
        self.serialComm = None

    def __getcrc(self, buf):
        temp = 0xffff
        for c in buf:
            i = ord(c)
            temp ^= i
            j = 1
            while j <= 8:
                flag = temp & 0x0001
                temp >>= 1
                if flag > 0:
                    temp ^= 0xa001
                j += 1
        temp2 = temp >> 8
        temp = (temp << 8) | temp2
        temp &= 0xffff
        print ('crc = ' + str(temp))
        return temp

    def addcrc(self, packet):
        crc = self.__getcrc(packet)
        return packet + chr(crc & 0xff) + chr(crc >> 8)

    def checkcrc(self, packet):
        tmpcrc = self.__getcrc(self.getmsgpart(packet))
        msgcrc = self.getcrcpart(packet)
        return (chr(tmpcrc >> 8) + chr(tmpcrc & 0xff)) == msgcrc

    def getcrcpart(self, packet):
        return packet[len(packet)-2:len(packet)]

    def getmsgpart(self, packet):
        return packet[0:len(packet)-2]

    def unslip(self, stream):
        packetlist = ''
        for char in stream:
            # cc = hex(ord(char))
            if char == self.SLIP_END:
                if self.started:
                    packetlist += self.packet
                else:
                    self.started = True
                self.packet = ''
            elif char == self.SLIP_ESC:
                self.escaped = True
            elif char == self.SLIP_ESC_END:
                if self.escaped:
                    self.packet += self.SLIP_END
                    self.escaped = False
                else:
                    self.packet += char
            elif char == self.SLIP_ESC_ESC:
                if self.escaped:
                    self.packet += self.SLIP_ESC
                    self.escaped = False
                else:
                    self.packet += char
            else:
                if self.escaped:
                    raise Exception('SLIP Protocol Error')
                    self.packet = ''
                    self.escaped = False
                else:
                    self.packet += char
                    self.started = True
        self.started = False
        return packetlist

    def slip(self, packet):
        encoded = self.SLIP_END
        for char in packet:
            # SLIP_END
            if char == self.SLIP_END:
                encoded += self.SLIP_ESC + self.SLIP_ESC_END
            # SLIP_ESC
            elif char == self.SLIP_ESC:
                encoded += self.SLIP_ESC + self.SLIP_ESC_ESC
            # the rest can simply be appended
            else:
                encoded += char
        encoded += self.SLIP_END
        return encoded
