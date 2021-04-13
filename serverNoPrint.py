import socket, struct, random, sys, os, threading
import senderNoPrint

PORT = 6666
userCount = 0

# connect with client
def connect( sock): 
    global userCount
    packet, addr1 = sock.recvfrom( 1040 )
    syn = format( struct.unpack( "!B", packet[14:15] )[0], '08b' )[1]
    # print( "Establishing connection with " + str( addr1 ) )
   
    # client asks for connection
    if( syn == '1' ):
        src = PORT
        dest = struct.unpack( "!H", packet[0:2] )[0]
        seqN = random.randint( 0, 9999 )
        ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
        window = seqN
        asf = int( '11000000', 2 )      # ack, syn, fin
        
        header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
        sock.sendto( header, addr1 )
        userCount += 1
        # print( "Acknowledgement sent to " + str( addr1 ) )

        packet, addr2 = sock.recvfrom( 1040 )
        ackN = struct.unpack( "!I", packet[8:12] )[0]
        ack = format( struct.unpack( "!B", packet[14:15] )[0], '08b' )[0]

        # client acknowledged handshake
        if( addr1 == addr2 and ackN == seqN + 1 and ack == "1" ):
            file = packet[16:].decode( 'utf-8' )
            path = sys.path[0] + "/serverStorage/" + file

            # file exist?
            if( os.path.isfile( path ) ):
                # print( "file found :) " )
                src = PORT
                dest = struct.unpack( "!H", packet[0:2] )[0]
                seqN += 1
                ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
                window += 1
                asf = int( '11000000', 2 )      # ack, syn, fin

                header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
                data = struct.pack( "!H", PORT + userCount )
                sock.sendto( header + data, addr2 )
                threading.Thread( target = senderNoPrint.send, args = ( addr2, header, userCount, path, ) ).start()
                # userCount -= 1
            
            else:
                # print( "file not found :(" )
                src = PORT
                dest = struct.unpack( "!H", packet[0:2] )[0]
                seqN += 1
                ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
                window += 1
                asf = int( '10100000', 2 )      # ack, syn, fin

                header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
                sock.sendto( header, addr2 )

                packet, addr3 = sock.recvfrom( 1040 )
                ackN = struct.unpack( "!I", packet[8:12] )[0]
                ack = format( struct.unpack( "!B", packet[14:15] )[0], '08b' )[0]

                if( addr2 == addr3 and ackN == seqN + 1 and ack == "1" ):
                    packet, addr4 = sock.recvfrom( 1040 )
                    ackN = struct.unpack( "!I", packet[8:12] )[0]
                    fin = format( struct.unpack( "!B", packet[14:15] )[2], '08b' )[0]

                    if( addr3 == addr4 and ackN == seqN + 1 and fin == "1" ):
                        src = PORT
                        dest = struct.unpack( "!H", packet[0:2] )[0]
                        seqN += 1
                        ackN = struct.unpack( "!I", packet[4:8] )[0] + 1
                        window += 1
                        asf = int( '10100000', 2 )      # ack, syn, fin
                        
                        header = struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )
                        sock.sendto( header, addr4 )
                        userCount -= 1



# listen for connection
def listenOn():
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( '', PORT ) )
    # print( "Listening on " + str( PORT )  )
    
    global userCount
    while 1:
        connect( sock)
        
        
def main():
    try:
        listenOn()
    except KeyboardInterrupt:
        # print( "\nThank you for using Coss Transport." )
        # print( "Exiting..." )
        sys.exit( 0 )

if __name__ == "__main__":
     main()
