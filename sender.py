import socket, struct, sys, time

def listenOn( port ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_RAW )
    sock.bind( ( '', port ) )
    print ( "Listening on " + str( port ) )

    while 1:
        recPacket, addr = sock.recvfrom(1024)
        i1, i2, i3, i4 = struct.unpack( "iiii", recPacket[20:36] )
        print( str( i1 ) + " " + str( i2 ) + " " + str( i3 ) + " " + str( i4 ) )

def main():
   listenOn( 6666 ) 


    

if __name__ == "__main__":
    main()
