import socket, os, sys

segment_size = 1024 + 16

class recvServer():
    def __init__(self, remote_port):
        self.remote_port = remote_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', self.remote_port))
        print('Local receiving server established, listening on %s' % self.remote_port)

        self.connections = {}
        
    def recvOneFile(self, fileName):
        flag = 1
        while flag:
            recvData, addr = self.socket.recvfrom(segment_size)
            
            

def recvFile(dest_port, fileName):
    recv_server = recvServer(dest_port)
    recv_server.recvOneFile(fileName)
