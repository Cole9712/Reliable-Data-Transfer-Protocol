import socket, os, sys, struct

seqNum = 0
source_Port = 9009

def setASFbyte(ack=0,syn=0,fin=0):
    # convert int to string and conbine
    byte = str(ack)+str(syn)+str(fin)+('00000')
    return int(byte, 2)

def main():

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
    _, _, seqNum, ackNum, _, asfByte = struct.unpack('!HHIIHBx', recvData)

    # check if ASF received byte is correct
    if asfByte != setASFbyte():
        print("ASF byte incorrect, connection fail to establish")
        sys.exit(1)
    
    # 3rd hand shake send (including fileName requested)
    packet = struct.pack('!HHIIHBx', source_Port, dest_port, ackNum+1 , seqNum+1, 0, setASFbyte(1,1,0))
    packet = packet + bytearray(filePath, 'utf-8')
    s.sendto(packet, (dest_ip, dest_port))
    print('HandShaking succeed! Request for file:' + filePath)

    



    
    

    
    


    


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("insufficient arguments")
        sys.exit(1)
    cmd = sys.argv[1]
    dest_ip = sys.argv[2]
    dest_port = int(sys.argv[3])
    filePath = sys.argv[4]
    main()