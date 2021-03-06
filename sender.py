import socket, struct, time, os, threading
import util


########## constants ##########


MSS = 1024

WINDOW_MAX_SIZE = 15

########## Variables ##########

TIMEOUT = 1
estimatedRTT = 1
devRTT = 0
segSent = 0
ackRecv = 0
currentAckN = 0     # acknowledge number to receiver
lastHeader = None   # reserved for header of the last segment

########## these need to be locked ##########

remote_buffer_size = 16*1024
cwnd = []           # sender window
mutex1 = threading.Semaphore(1)
full1 = threading.Semaphore(0)
empty1 = threading.Semaphore(15)
mutex2 = threading.Semaphore()
mutex3 = threading.Semaphore()
localWindow = 2

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
        print( "Error: No data read")
        return False


# send the next segment of file
def sendNextSegment( sock, addr, file, header ) -> None:
    global lastHeader
    global currentAckN
    global segSent
    global cwnd
    while( not file.closed ):
        segment = file.read( MSS )

        # file not empty
        if( len( segment ) != 0 ):
            # lock
            header = util.nextHeader( header, newAckN = currentAckN)
            
            empty1.acquire()
            mutex1.acquire()
            cwnd.append( packet( header, segment ) )
            segSent += 1
            mutex1.release()
            full1.release()
            
            # print(remote_buffer_size)

            while remote_buffer_size <= 6144:
                print('remote buffer size about to overflow, flow control involved, remote buffer free size=' + str( remote_buffer_size ))
                time.sleep(estimatedRTT)

            while localWindow < len(cwnd):
                print('congestion control involved')
                time.sleep(estimatedRTT)
            sock.sendto( header + segment, addr )
            # print( "Segment sent with sequence number: " + str( util.getHeader( header, seqN = True ) ) )

        else:
            file.close()
            # thread finished
    print( header )
    lastHeader = header


# send a timeout segment of file
def sendLostSegment( sock, addr, file ) -> None:
    global currentAckN
    global TIMEOUT
    global localWindow
    # cwnd not empty
    while True:
        flag = False

        # transmission timeout
        mutex2.acquire()
        TO = TIMEOUT
        mutex2.release()

        mutex1.acquire()
        length = len( cwnd )
        if file.closed and length == 0 :
            print('lost thread closed')
            return None
        if( length > 0 ):
            timestamp = cwnd[0].timestamp
            lostHeader = cwnd[0].header
            lostSeqN = cwnd[0].getSeqN()
            lostData = cwnd[0].data
            diffTime = time.time() - timestamp
            if( diffTime > TO ):
                cwnd[0].timestamp = time.time()
                mutex1.release()
                flag = True
                mutex3.acquire()
                localWindow = localWindow/2
                mutex3.release()
            else:
                mutex1.release()
                # time.sleep(TO - diffTime)
                time.sleep(0.3)
                continue
        else:
            mutex1.release()


        if flag:
            print("TIMEOUT with {0}".format(TO))
            # congestion control invoked by timeout, divide cwnd by 2
            # empty1._value = int(empty1._value / 2)

            newHeader = util.nextHeader( lostHeader, newSeqN = lostSeqN, newAckN = currentAckN )
            sock.sendto( newHeader + lostData, addr )

            print( "Lost segment sent with sequence number: " + str( util.getHeader( newHeader, seqN = True ) ) )



########## ack listener ##########


# listen for incoming ack
def listenForAck( sock, file ) -> None:
    global currentAckN
    global ackRecv
    global remote_buffer_size
    global estimatedRTT
    global devRTT
    global TIMEOUT
    global cwnd
    global localWindow
    while True:

        if ( file.closed and ackRecv == segSent ):
            return None

        # listen for new packet
        packet, addr = sock.recvfrom( 1040 )
        recvSeqN, recvAckN, remote_buffer_size, recvAck = util.getHeader( packet[0:16], seqN = True, ackN = True, window = True, ack = True )        
        
        # is ack 
        if( recvAck == 1 ):
            currentAckN = recvSeqN + 1
            
            print( "Segment ACKed with sequence number: " + str( recvAckN - 1 ) )

            # discard acked packet from window
            flag = False
            mutex1.acquire()
            localCwnd = cwnd
            mutex1.release()
            for i in range( len( localCwnd ) ):
                if( localCwnd[i].getSeqN() == recvAckN - 1 ):
                    # calculate RTT
                    sampleRTT = time.time() - localCwnd[i].timestamp
                    print('poped seq No.{0}'.format(localCwnd[i].getSeqN()))
                    j = i
                    flag = True
                    ackRecv += 1
                    break
            if flag:
                full1.acquire()
                mutex1.acquire()
                cwnd.pop( j )
                mutex1.release()
                empty1.release()
                # congestion control, append window size by 1
                if localWindow < WINDOW_MAX_SIZE and j==0:
                    mutex3.acquire()
                    localWindow += 1
                    mutex3.release()
                
            estimatedRTT = 0.875*estimatedRTT + 0.125*sampleRTT
            devRTT = 0.75*devRTT + 0.25*abs(sampleRTT - estimatedRTT)
            # lock
            mutex2.acquire()
            TIMEOUT = estimatedRTT + 4*devRTT
            mutex2.release()
            


########## main functions ##########


# sends file -> ( sent successful?, header )
def sendFile( sock, addr, header, path ) -> bytes:
    # open file
    file = open( path, "rb" )   # rb = read-only, binary
    # create threads
    nextSeg = threading.Thread( target = sendNextSegment, args = ( sock, addr, file, header, ) )
    lostSeg = threading.Thread( target = sendLostSegment, args = ( sock, addr, file) )
    ackListener = threading.Thread( target = listenForAck, args = ( sock, file ) )
    
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

    print( lastHeader )
    seqN = util.getHeader( lastHeader, seqN = True )[0]
    header = util.nextHeader( lastHeader, newSeqN = seqN, newAckN = currentAckN)
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
        header = util.nextHeader( header, newSeqN = seqN + 1, newAckN = currentAckN)
        
        # send file in truncks
        print( "Start sending file..." )
        sucHeader = sendFile( sock, addr, header, path )
        print( "All segment transmitted!" )

        # send fin bit to prompt to close
        header = util.nextHeader( sucHeader, asf = "001" )
        sock.sendto( header, addr )

        ack = 0
        start = time.time()
        while( ack == 1 or time.time() - start > 2 ):
            packet, addr = sock.recvfrom( 1024 )
            ack = util.getHeader( packet[0:16], ack = True )
        sock.close()


def main():
    return


if __name__ == "__main__":
    main()
