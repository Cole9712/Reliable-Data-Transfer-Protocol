import socket, os, sys, struct, receiver
from util import setASFbyte

seqNum = 0
source_Port = 9009

def main(cmd, dest_ip, dest_port, filePath, seqNum = 0):

    # show local file path
    print("Received File Path is " + filePath)

    # start HandShaking
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(('', source_Port))
    except socket.error as msg:
        print('port binding error: %s' % msg)

    packet = struct.pack('!HHIIHBx', source_Port, dest_port, seqNum, 0, 0, setASFbyte(0,1,0))
    s.sendto(packet, (dest_ip, dest_port))
    recvData, _ = s.recvfrom(1040)
    seqNum = struct.unpack('!I', recvData[4:8])[0]
    ackNum = struct.unpack('!I', recvData[8:12])[0]
    asfByte = struct.unpack('!B', recvData[14:15])[0]

    # check if ASF received byte is correct
    if asfByte != setASFbyte(1,1,0):
        print("ASF byte incorrect, connection fail to establish")
        sys.exit(1)
    
    # 3rd hand shake send (including fileName requested)
    packet = struct.pack('!HHIIHBx', source_Port, dest_port, ackNum+1 , seqNum+1, 0, setASFbyte(1,1,0))
    packet = packet + bytearray(filePath, 'utf-8')
    s.sendto(packet, (dest_ip, dest_port))
    print('HandShaking succeed! Request for file:' + filePath)

    # recv from server if file exists
    # Check if file exists
    recvData, _ = s.recvfrom(1040)
    dest_port = struct.unpack('!H', recvData[0:2])[0]
    asfByte = struct.unpack('!B', recvData[14:15])[0]

    # check FIN bit to see if file exists
    if format(asfByte, '08b')[2:3] == '1':
        print('No such file on server, connection close!')
        return

    # Start transfer the file
    print("Starting tranferring file...")
    s.close()
    receiver.recvFile(source_Port, filePath)



if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("insufficient arguments")
        sys.exit(1)
    cmd = sys.argv[1]
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    filePath = sys.argv[4]
    main(cmd, dest_ip, dest_port, filePath)
