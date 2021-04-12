import socket, struct, time, os, threading
import util


########## constants ##########


MSS = 1024
TIMEOUT = 1     # !!! implement variation timeout later...


########## these need to be locked ##########


cwnd = []           # sender window
currentAckN = 0     # acknowledge number to receiver
lastHeader = None   # reserved for header of the last segment 


########## packet class for cwnd record ##########


class packet:
    def __init__( self, header, data ) -> None:
        self.timestamp = time.time()
        self.header = header
        self.data = data

    def getSeqN( self ) -> int:
        return util.getHeader( self.header, seqN = True )[0]


########## segment transmission threads ##########


# send the first segment of file -> sent successful?
def sendFirstSegment( sock, addr, file, header ) -> bool:
    segment = file.read( MSS )

    if( len( segment ) != 0 ):
        header = util.nextHeader( header, newAckN = currentAckN )
        cwnd.append( packet( header, segment ) )
        sock.sendto( header + segment, addr )
        print( "First segment sent with sequence number: " + str( util.getHeader( header, seqN = True ) ) )
        return True
    else:
        file.close()
        print( "Error: No data read" )
        return False


# send the next segment of file
def sendNextSegment( sock, addr, file, header ) -> None:
    while( not file.closed ):
        segment = file.read( MSS )

        # file not empty
        if( len( segment ) != 0 ):

            # cwnd not empty
            # lock
            if( len( cwnd ) != 0 ):
                header = util.nextHeader( header, newAckN = currentAckN, newWindow = cwnd[0].getSeqN() )
            else:
                header = util.nextHeader( header, newAckN = currentAckN, newWindow = util.getHeader( header, seqN = True)[0] + 1 )
            # release
            cwnd.append( packet( header, segment ) )
            sock.sendto( header + segment, addr )
            print( "Segment sent with sequence number: " + str( util.getHeader( header, seqN = True ) ) )
        else:
            file.close()
            # thread finished
    lastHeader = header


# send a timeout segment of file
def sendLostSegment( sock, addr ) -> None:
    # cwnd not empty
    # lock
    while( len( cwnd ) != 0 ):
        # transmission timeout
        if( time.time() - cwnd[0].timestamp > TIMEOUT ):
            newHeader = util.nextHeader( cwnd[0].header, newSeqN = cwnd[0].getSeqN(), newAckN = currentAckN )
            sock.sendto( newHeader + cwnd[0].data, addr )
            print( "Lost segment sent with sequence number: " + str( util.getHeader( newHeader, seqN = True ) ) )
        # release
        time.sleep( 1 )
        # lock

    # release
    return None


########## ack listener ##########


# listen for incoming ack
def listenForAck( sock ) -> None:
    # cwnd not empty
    # lock
    while( len( cwnd ) != 0 ):
        # release
        # listen for new packet
        packet, addr = sock.recvfrom( 1040 )
        recvSeqN, recvAckN, recvAck = util.getHeader( packet[0:16], seqN = True, ackN = True, ack = True )        
        
        # is ack 
        if( recvAck == 1 ):
            # lock
            currentAckN = recvSeqN + 1
            
            print( "Segment ACKed with sequence number: " + str( recvAckN - 1 ) )

            # discard acked packet from window
            for i in range( len( cwnd ) ):
                if( cwnd[i].getSeqN() == recvAckN - 1 ):
                    cwnd.pop( i )
                    # release
                    break

    # release
    return None


########## main functions ##########


# sends file -> ( sent successful?, header )
def sendFile( sock, addr, header, path ) -> bytes:
    # open file
    file = open( path, "rb" )   # rb = read-only, binary
    
    # create threads
    nextSeg = threading.Thread( target = sendNextSegment, args = ( sock, addr, file, header, ) )
    lostSeg = threading.Thread( target = sendLostSegment, args = ( sock, addr, ) )
    ackListener = threading.Thread( target = listenForAck, args = ( sock, ) )
    
    # start threads
    print( "Starting threads..." )
    nextSeg.start()
    lostSeg.start()
    ackListener.start()

    # threads finished
    nextSeg.join()
    lostSeg.join()
    ackListener.join()
    print( "Threads finished" )
    
    seqN = util.getHeader( lastHeader, seqN = True )
    header = util.nextHeader( lastHeader, newSeqN = seqN, newAckN = currentAckN, newWindow = util.getHeader( lastHeader, seqN = True )[0] + 1 )
    return header


# sends file
def send( addr, header, userCount, path ):
    time.sleep( 2 )
    src, dest, seqN, ackN, window, _, _, _ = util.unpackHeader(header)
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( '', src + userCount  ) )

    # initial packet with file size
    header = util.makeHeader( src + userCount, dest, seqN + 1, ackN, window + 1, int( "01000000", 2 ) )
    data = struct.pack( "!I", os.path.getsize( path ) )
    sock.sendto( header + data, addr )
    print( "Initial packet with file size sent" )

    # receive ack from client with port switch
    packet, addr = sock.recvfrom( 1040 )
    recvSeqN, recvAckN, recvAck = util.getHeader( packet[0:16], seqN = True, ackN = True, ack = True )
    print( "seqN = " + str( recvSeqN ) + " ackN = " + str( recvAckN ) + " ack = " + str( recvAck ) )
    print( "mySeqN" + str( seqN + 2 ) )

    if( recvAckN == seqN + 2 and recvAck == 1 ):
        print( "File size acknowledged" )
        # update window for recieving ack
        currentAckN = recvSeqN + 1
        header = util.nextHeader( header, newSeqN = seqN + 1, newAckN = currentAckN, newWindow = window + 2 )
        
        # send file in truncks
        print( "Start sending file..." )
        sucHeader = sendFile( sock, addr, header, path )
        print( "All segment transmitted!" )

        # send fin bit to prompt to close
        header = util.nextHeader( sucHeader, asf = "001" )
        sock.sendto( header, addr )

        ack = 0
        start = time.time()
        while( ack != 1 or time.time() - start > 2 ):
            packet, addr = sock.recvfrom( 1024 )
            ack = util.getHeader( packet[0:16], ack = True )
        sock.close() 


def main():
    return


if __name__ == "__main__":
    main()
