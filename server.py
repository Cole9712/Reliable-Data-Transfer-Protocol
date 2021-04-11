import socket, struct, random
import sender

PORT = 6666

# connect with client
def connect( sock, userCount ): 
    packet, addr = sock.recvfrom( 1040 )
    syn = format( struct.unpack( "!B", packet[14] )[0], '08b' )[1]
    print( "Establishing connection with " + addr )
   
    # client asks for connection
    if( syn == '1' ):
        src = PORT
        dest = struct.unpack( "!H", packet[0:2] )[0]
        seqN = random.randint( 0, 9999 )
        ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
        window = 0
        asf = int( '11000000', 2 )      # ack, syn, fin
        
        header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
        sock.sendto( header, addr )
        userCount += 1
        print( "Acknowledgement sent to " + addr )

        packet, addr = sock.recvfrom( 1040 )
        ackN = struct.unpack( "!I", packet[8:12] )[0]
        ack = struct.unpack( "!B", packet[14:15] )[0][0]

        # client acknowledged handshake
        if( ackN == seqN + 1 and ack == "1" ):
            file = packet[16:].decode( 'uft-8' )

            # file exist?
            if( sender.validate( file ) ):
                print( "file found :) " )
                src = PORT
                dest = struct.unpack( "!H", packet[0:2] )[0]
                seqN += 1
                ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
                window += 1
                asf = int( '11000000', 2 )      # ack, syn, fin

                header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
                data = struct.pack( "!H", PORT + userCount )
                sock.sendto( header + data, addr )
            
            else:
                # ignore client
                userCount -= 1
                print( "file not find :(" )


# listen for connection
def listenOn():
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( '', PORT ) )
    print( "Listening on " + str( PORT )  )
    
    userCount = 0
    while 1:
        connect( sock, userCount )
        
        
def main():
   listenOn()
 

if __name__ == "__main__":
     main()
