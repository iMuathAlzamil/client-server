class Packet:
    def __init__(self, seqNum, actionNum, payload):
        self.seqNum = seqNum
        self.actionNum = actionNum
        self.length = len(payload)
        self.payload = payload

    def createPacket(self):
        seq = '{:04x}'.format(self.seqNum)
        action = '{:01x}'.format(self.actionNum)
        length = '{:03x}'.format(self.length)
        bArray = bytearray(seq + action + length + self.payload, 'utf-8')
        return bArray
    
    def unpackPacket(self, pktString):
        self.seq = int(pktString[0:4].decode("utf-8"), 16)
        self.action = int(pktString[4:5].decode("utf-8"), 16)
        self.length = int(pktString[5:8].decode("utf-8"), 16)
        self.payload = pktString[8:].decode("utf-8")

    def toString(self):
        return 'Packet Data: Seq = {0}, Action = {1}, Length = {2}, Payload = {3}'.format(self.seqNum, self.actionNum, self.length, self.payload)

def testPacket():
    pkt = Packet(2, 1, 'Hello World')
    code = pkt.createPacket()
    print('Encoded String: {0}'.format(code))
    pkt.unpackPacket(code)
    print('Decoded String: {0}'.format(pkt.toString()))
    
#testPacket()
