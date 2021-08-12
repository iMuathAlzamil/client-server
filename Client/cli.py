from packet import Packet

import threading
import random
import sys
import socket
import math
import os.path

MAX_SIZE_OF_BUFFER = 1032

def main(argv):
    if(len(argv) != 2):
        print('Error: Must be called as: python cli.py <server host> <port number>')
        return 2
    else:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = int(argv[1])
        hst = argv[0]

        skt.connect((hst, port))
        print('Client Is Connected...')
        while(True):
            command = input("ftp> ")
            if(command.startswith('get')):
                print('Receiving Server File')
                pkt = Packet(0, 0, '')
                bArray = pkt.createPacket()
                skt.send(bArray)
                
                pktString = skt.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)
                
                print('Client Trying to Connect To Port {0}'.format(int(pkt.payload)))
                dataSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                dataSkt.connect((hst, int(pkt.payload)))
                
                fileName = command[4:]
                pkt = Packet(0, 0, fileName)
                dataSkt.send(pkt.createPacket())

                pktString = dataSkt.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)

                if(pkt.payload.startswith('Error:')):
                    print('FAILURE: Could Not Find File {0}'.format(fileName))
                else:
                    info = pkt.payload.split('\n')
                    fileName = info[0]
                    numPackets = int(math.ceil(int(info[1]) / 1024.0))
                    
                    dataTable = {}
                    while(len(dataTable) < numPackets):
                        pktString = dataSkt.recv(MAX_SIZE_OF_BUFFER)
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
                dataSkt.close()
            elif(command.startswith('put')):
                if(os.path.exists(command[4:])):
                    print('Sending New File')
                    pkt = Packet(0, 1, '')
                    bArray = pkt.createPacket()
                    skt.send(bArray)
                    
                    pktString = skt.recv(MAX_SIZE_OF_BUFFER)
                    pkt = Packet(0, 1, '')
                    pkt.unpackPacket(pktString)
                    
                    print('Client Trying to Connect To Port {0}'.format(int(pkt.payload)))
                    dataSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                    dataSkt.connect((hst, int(pkt.payload)))
                    
                    fileName = command[4:]
                    handle = open(fileName, 'r')
                    data = handle.read()
                    size = len(data)
                    pkt = Packet(0, 1, fileName + '\n' + str(size))
                    dataSkt.send(pkt.createPacket())

                    print('Starting To Send Data...')
                    for i in range(0, size, 1024):
                        if(i + 1024 < size):
                            pktData = data[i:i+1024]
                        else:
                            pktData = data[i:size]
                        pkt = Packet(int(i/1024), 1, pktData)
                        print('Sending Packet {0}, Data = {1}'.format(int(i/1024), pktData))
                        dataSkt.send(pkt.createPacket())
                    print('SUCCESS: File {0} Sent {1} bytes'.format(fileName, size))
                    dataSkt.close()
                else:
                    print('FAILURE: Cannot Find File {0}'.format(command[4:]))
            elif(command.startswith('ls')):
                print('LS Operation')
                pkt = Packet(0, 2, '')
                bArray = pkt.createPacket()
                skt.send(bArray)

                pktString = skt.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)
                
                print('Client Trying to Connect To Port {0}'.format(int(pkt.payload)))
                dataSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                dataSkt.connect((hst, int(pkt.payload)))
                
                pktString = dataSkt.recv(MAX_SIZE_OF_BUFFER)
                pkt = Packet(0, 0, '')
                pkt.unpackPacket(pktString)
                info = pkt.payload.split('\n')
                numPackets = int(math.ceil(int(info[1]) / 1024.0))
                    
                dataTable = {}
                while(len(dataTable) < numPackets):
                    pktString = dataSkt.recv(MAX_SIZE_OF_BUFFER)
                    pkt = Packet(0, 0, '')
                    pkt.unpackPacket(pktString)
                    dataTable[pkt.seq] = pkt.payload
                print('# Packets Received: {0}'.format(len(dataTable)))
                data = ''
                for i in range(0, numPackets):
                    data += dataTable[i]
                print(data)
                print('SUCCESS: Received {0} bytes'.format(len(data)))
                dataSkt.close()
            elif(command.startswith('quit')):
                pkt = Packet(0, 3, 'Quitting')
                skt.send(pkt.createPacket())
                break
            else:
                print('Unknown Operations: Try get, put, ls, or quit')
        skt.close()
        return 0

if __name__ == "__main__":
    main(sys.argv[1:])
