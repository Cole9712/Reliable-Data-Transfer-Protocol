import socket, os, sys, struct

segment_size = 1024 + 16



# unpack header information according to protocol design in README.md
def unpackHeader(header):
    source_port = struct.unpack('!H', header[0:2])[0]
    dest_port = struct.unpack('!H', header[2:4])[0]
    seqNum = struct.unpack('!I', header[4:8])[0]
    ackNum = struct.unpack('!I', header[8:12])[0]
    asfByte = struct.unpack('!B', header[14:15])[0]
    ACK = int(format(asfByte, '08b')[0:1])
    SYN = int(format(asfByte, '08b')[1:2])
    FIN = int(format(asfByte, '08b')[2:3])
    return source_port, dest_port, seqNum, ackNum, ACK, SYN, FIN

class RecvServer(object):
    def __init__(self, remote_port):
        self.remote_port = remote_port
        self.rcvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rcvSocket.bind(('127.0.0.1', self.remote_port))
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print('Local receiving server established, listening on %s' % self.remote_port)
        
    def rcvOneSegment(self, rcvData, remote_addr):
        remote_port, local_port, seqNum, ackNum, ACK, SYN, FIN = unpackHeader(rcvData)
        payload = rcvData[16:]


        # check if first segment
        if SYN == 1:
            self.fileSize = payload.decode()
            fileSizeInMb = self.fileSize / 1048576
            print('Start to receive file: {0} with size {1} MB from {2}'.format(self.fileName, fileSizeInMb, remote_addr))
            self.nextSeq = ackNum
            self.nextAck = seqNum + 1

        elif len(self.rcvBuffer) < self.bufferMaxSize and seqNum >= self.nextSeq:
            # locate the recvData's position in buffer
            

            
        


    def recvOneFile(self, fileName):
        self.transEnd = False
        self.fileName = fileName
        # Suppose max size buffer can handle is 8192 bytes = 8 segments
        self.bufferMaxSize = 8
        self.rwnd = 8192
        # rcvBuffer stores array of received (header, data)
        self.rcvBuffer = []
        self.fileSize = 0
        self.packetCount = 0

        while not self.end:
            recvData, addr = self.rcvSocket.recvfrom(segment_size)
            self.rcvOneSegment(recvData, addr)


            
            

def recvFile(dest_port, fileName):
    recv_server = RecvServer(dest_port)
    recv_server.recvOneFile(fileName)
