import socket, struct, sys, time

def listenOn( port ):
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( '', port ) )
    print ( "Listening on " + str( port ) )

    while 1:
        recPacket, addr = sock.recvfrom( 1024 )


def main():
   listenOn( 6666 ) 
 

if __name__ == "__main__":
    main()
