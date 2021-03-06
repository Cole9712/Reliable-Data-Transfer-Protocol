import socket, os, sys, struct, client
from util import unpackHeader, packHeader

segment_size = 1024 + 16

class RecvObject(object):
    def __init__(self, seqNum, fin, data):
        self.seqNum = seqNum
        self.FIN = fin
        self.data = data

class RecvServer(object):
    def __init__(self, remote_port):
        self.remote_port = remote_port
        self.rcvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rcvSocket.bind(('', remote_port))

        print('Local receiving server established, listening on %s' % self.remote_port)

    def sendACK(self, remote_addr):
        packet = packHeader(0, self.remote_port, self.nextSendSeq, self.nextSeq, self.rwnd, 1, 0, self.finBit)
        self.rcvSocket.sendto(packet, remote_addr)
        
    def rcvOneSegment(self, rcvData, remote_addr):
        remote_port, local_port, seqNum, ackNum, _, ACK, SYN, FIN = unpackHeader(rcvData)
        payload = rcvData[16:]
        print('Received segment with seqNum {0}'.format(seqNum))


        # check if first segment
        if SYN == 1:
            size = struct.unpack('!I', payload)[0]
            self.fileSize = size
            fileSizeInMb = self.fileSize / 1048576
            print('Start to receive file: {0} with size {1} MB from {2}'.format(self.fileName, fileSizeInMb, remote_addr))
            self.file = open(self.fileName, 'wb')
            self.nextSendSeq = ackNum
            self.nextSeq = seqNum + 1
            self.sendACK(remote_addr)

        elif len(self.rcvBuffer) < self.bufferMaxSize and seqNum >= self.nextSeq:
            
            self.nextSendSeq = ackNum
            # locate the recvData's position in buffer
            i = 0
            while i < len(self.rcvBuffer) and self.rcvBuffer[i].seqNum < seqNum:
                i+=1
            
            # check if received is duplicated packet
            if len(self.rcvBuffer) != 0 and len(self.rcvBuffer) != i:
                if (self.rcvBuffer[i].seqNum == seqNum):
                    return

            self.rcvBuffer.insert(i, RecvObject(seqNum, FIN, payload))
            self.rwnd -= 1024

            # check FIN bit
            if FIN == 1:
                self.finBit = 1
                self.file.close()
                self.transEnd = True
                print('All packets received successfully. Closing Connection...')
                self.sendACK(remote_addr)
                return
            
            j = 0
            while j< len(self.rcvBuffer) and self.rcvBuffer[j].seqNum == self.nextSeq:
                
                self.rwnd += 1024
                self.nextSeq += 1
                self.sendACK(remote_addr)
                self.file.write(self.rcvBuffer[j].data)
                self.packetCount += 1
                print('Writing packet No.{0} into destination file'.format(self.packetCount))
            
                j += 1

            self.rcvBuffer = self.rcvBuffer[j:]
            
            # check if buffer is full
            # if full, pop the last element
            if len(self.rcvBuffer) == self.bufferMaxSize:
                self.rcvBuffer.pop()
                self.rwnd += 1024
        elif seqNum < self.nextSeq:
            tmp = self.nextSeq
            self.nextSeq = seqNum + 1
            print('Sent old ACK with ackNum {0}'.format(self.nextSeq))
            self.sendACK(remote_addr)
            self.nextSeq = tmp



    def recvOneFile(self, fileName):
        self.transEnd = False
        self.fileName = fileName
        # Suppose max size buffer can handle is 8192 bytes = 8 segments
        self.bufferMaxSize = 16
        self.rwnd = 8192*2
        # rcvBuffer stores array of received in the format RecvObject
        self.rcvBuffer = []
        self.fileSize = 0
        self.packetCount = 0
        self.finBit = 0

        while not self.transEnd:
            recvData, addr = self.rcvSocket.recvfrom(segment_size)
            self.rcvOneSegment(recvData, addr)

            

def recvFile(dest_port, fileName):
    recv_server = RecvServer(dest_port)
    recv_server.recvOneFile(fileName)
