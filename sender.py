import socket, struct, time, os

MSS = 1024


# pack header into binary string
def makeHeader( src, dest, seqN, ackN, window, asf ):
    return struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )


# receive specific elements from the header
def getHeader( header, src = False, dest = False, seqN = False, ackN = False,
        window = False, ack = False, syn = False, fin = False ):
    hsrc, hdest, hseqN, hackN, hwindow, hasf = struct.unpack( "!HHIIHBx", header )
    hack = format( hasf, '08b' )[0]
    hsyn = format( hasf, '08b' )[1]
    hfin = format( hasf, '08b' )[2]

    res = ()
    
    if( src ): res += ( hsrc, )
    if( dest ): res += ( hdest, )
    if( seqN ): res += ( hseqN, )
    if( ackN ): res += ( hackN, )
    if( window ): res += ( hwindow, )
    if( ack ): res += ( hack, )
    if( syn ): res += ( hsyn, )
    if( fin ): res += ( hfin, )

    return res


# prepares next packet's header
def nextHeader( prev, newAckN = 0, recvAck = 0, asf = "000" ):
    src, dest, seqN, ackN, window = struct.unpack( "!HHIIH", prev )
    seqN += 1
    ackN = newAckN if newAckN != 0 else ackN
    window += recvAck
    asf = int( asf + "00000", 2 )
    return makeHeader( src, dest, seqN, ackN, window, asf )


# sends file
def sendFile( sock, addr, header, path ):
    file = open( path, "rb" )

    isSending = True
    while( isSending ):
        # send 5 segments
        for i in range( 5 ):
            segment = file.read( MSS )

            if( len( segment ) != 0 ):
                header = nextHeader( header )
                sock.sendto( header + segment, addr )
            else:
                file.colse()
                isSending = False
                break

        # listen for 5 acks
        recvAck = 0
        for j in range( i + 1 ):
            packet, addr = sock.recvfrom( 1040 )
# pick up here!!!!!!



# sends file
def send( addr, header, userCount, path ):
    time.sleep( 2 )
    src, dest, seqN, ackN, window = struct.unpack( "!HHIIH", header )
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( '', src + userCount  ) )

    # initial packet with file size
    header = makeHeader( src + userCount, dest, seqN + 1, ackN, window, int( "00000000", 2 ) )
    data = struct.pack( "!I", os.path.getsize( path ) )
    sock.sendto( header + data, addr )

    # receive ack from client
    packet, addr = sock.recvfrom( 1040 )
    if( getHeader( packet[0:16], ack = True )[0] ):
        # send file in truncks
        sendFile( sock, addr, header, path )

    

def main():
    a = 1


if __name__ == "__main__":
    main()
