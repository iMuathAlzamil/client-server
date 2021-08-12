from packet import Packet

import threading
import random
import sys
import socket
import math
import os.path
import subprocess

MAX_SIZE_OF_BUFFER = 1032

portLock = threading.Lock()
threadLock = threading.Lock()

ephimeralPorts = {}
sockets = []
        
class ServerThread(threading.Thread):
    def __init__(self, addrSKT, addrIP, addrPORT):
        threading.Thread.__init__(self)
        print('Thread Created For: Addr = {0} @ Port = {1}'.format(addrIP, addrPORT))
        self.myIP = addrIP
        self.mySKT = addrSKT
        self.myPORT = addrPORT
        
    def run(self):
        while(True):
            pktString = self.mySKT.recv(MAX_SIZE_OF_BUFFER)
            pkt = Packet(0, 0, '')
            pkt.unpackPacket(pktString)
            if(pkt.action == 0):
                ePort = getEphimeralPort(self.myIP)
                
                newSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                newSkt.bind((self.myIP, ePort))
                pkt = Packet(0, 5, str(ePort))
                self.mySKT.send(pkt.createPacket())
                
                print('Server Is Connecting...')
                newSkt.listen(5)
                (connection, (addr, prt)) = newSkt.accept()
                print('Server Accepted Connection From {0} @ {1} (Data)'.format(addr, prt))

                pktString = connection.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)
                
                print('Begin Sending Data From Client {0} @ {1} ...'.format(addr, prt))
                fileName = pkt.payload

                if(os.path.exists(fileName)):
                    handle = open(fileName, 'r')
                    data = handle.read()
                    size = len(data)
                    pkt = Packet(0, 0, fileName + '\n' + str(size))
                    connection.send(pkt.createPacket())

                    print('Starting To Send Data...')
                    for i in range(0, size, 1024):
                        if(i + 1024 < size):
                            pktData = data[i:i+1024]
                        else:
                            pktData = data[i:size]
                        pkt = Packet(int(i/1024), 0, pktData)
                        print('Sending Packet {0}, Data = {1}'.format(int(i/1024), pktData))
                        connection.send(pkt.createPacket())
                    print('Success: File {0} Sent {1} bytes'.format(fileName, size))
                else:
                    pkt = Packet(0, 0, 'Error: Cannot Find File')
                    connection.send(pkt.createPacket())
                    print('Failure: File {0} Could Not Be Found'.format(fileName))
                releaseEphimeralPort(ePort)
                connection.close()
            elif(pkt.action == 1):
                ePort = getEphimeralPort(self.myIP)
                
                newSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                newSkt.bind((self.myIP, ePort))
                pkt = Packet(0, 5, str(ePort))
                self.mySKT.send(pkt.createPacket())
                
                print('Server Is Connecting...')
                newSkt.listen(5)
                (connection, (addr, prt)) = newSkt.accept()
                print('Server Accepted Connection From {0} @ {1} (Data)'.format(addr, prt))

                pktString = connection.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)
                
                print('Begin Receiving Data From Client {0} @ {1} ...'.format(addr, prt))
                info = pkt.payload.split('\n')
                fileName = info[0]
                numPackets = int(math.ceil(int(info[1]) / 1024.0))
                
                dataTable = {}
                while(len(dataTable) < numPackets):
                    pktString = connection.recv(MAX_SIZE_OF_BUFFER)
                    pkt = Packet(0, 0, '')
                    pkt.unpackPacket(pktString)
                    dataTable[pkt.seq] = pkt.payload
                    print('# Packets Received: {0}'.format(len(dataTable)))
                data = ''
                for i in range(0, numPackets):
                    data += dataTable[i]
                print('Creating file {0}'.format(fileName))
                handle = open(fileName, "w")
                handle.write(data)
                handle.close()
                print('SUCCESS: File {0} Created.'.format(fileName))
                releaseEphimeralPort(ePort)
                connection.close()
            elif(pkt.action == 2):
                data = subprocess.check_output('ls', shell=True)
                ePort = getEphimeralPort(self.myIP)
                
                newSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                newSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                newSkt.bind((self.myIP, ePort))
                pkt = Packet(0, 5, str(ePort))
                self.mySKT.send(pkt.createPacket())
                
                print('Server Is Connecting...')
                newSkt.listen(5)
                (connection, (addr, prt)) = newSkt.accept()
                print('Server Accepted Connection From {0} @ {1} (Data)'.format(addr, prt))

                print('Begin Sending Data From Client {0} @ {1} ...'.format(addr, prt))
                size = len(data)
                pkt = Packet(0, 0, 'ls\n' + str(size))
                connection.send(pkt.createPacket())

                print('Starting To Send Data...')
                for i in range(0, size, 1024):
                    if(i + 1024 < size):
                        pktData = data[i:i+1024].decode("utf-8") 
                    else:
                        pktData = data[i:size].decode("utf-8") 
                    pkt = Packet(int(i/1024), 0, pktData)
                    print('Sending Packet {0}, Data = {1}'.format(int(i/1024), pktData))
                    connection.send(pkt.createPacket())
                print('Success: LS Operation, Sent {0} bytes'.format(size))
                releaseEphimeralPort(ePort)
                connection.close()
            elif(pkt.action == 3):
                print('Closed On {0}'.format(self.myPORT))
                self.mySKT.close()
                break

def createEphimeralPort():
    for i in range(49152, 65536):
        ephimeralPorts[i] = None
    
def getEphimeralPort(ip):
    port = 0
    portLock.acquire()
    while(True):
        port = random.randint(49152, 65535)
        if(ephimeralPorts[port] is None):
            ephimeralPorts[port] = ip
            break
    portLock.release()
    return port

def releaseEphimeralPort(port):
    portLock.acquire()
    ephimeralPorts[port] = None
    portLock.release()

def main(argv):
    if(len(argv) != 1):
        print('Error: Must be called as: python serv.py <port number>')
        return 2
    else:
        createEphimeralPort()
        port = int(argv[0])
        hst = socket.gethostname()

        print(hst)
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        skt.bind((hst, port))
        print('Server Is Connected...')
        while(True):
            skt.listen(1)
            print('Server Is Waiting For A Client...')
            (connection, (addr, prt)) = skt.accept()
            print('Server Accepted Connection From {0}', addr)
            th = ServerThread(connection, addr, prt)
            th.start()

if __name__ == "__main__":
    main(sys.argv[1:])
