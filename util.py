import struct

# pack header into binary string
def makeHeader( src, dest, seqN, ackN, window, asf ) -> bytes:
    return struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )


# receive specific elements from the header
def getHeader( header, src = False, dest = False, seqN = False, ackN = False,
        window = False, ack = False, syn = False, fin = False ) -> tuple:
    hsrc, hdest, hseqN, hackN, hwindow, hack, hsyn, hfin = unpackHeader( header )

    res = tuple()
    
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
def nextHeader( prev, newSeqN = 0, newAckN = 0, newWindow = 0, asf = "000" ) -> bytes:
    src, dest, seqN, ackN, window, ack, syn, fin = unpackHeader( prev )
    seqN = newSeqN if newSeqN != 0 else seqN + 1
    ackN = newAckN if newAckN != 0 else ackN
    window = newWindow if newWindow != 0 else window
    asf = int( asf + "00000", 2 )
    return makeHeader( src, dest, seqN, ackN, window, asf )

def packHeader(source_port, dest_port, seqNum, ackNum, window, ACK, SYN, FIN):
    return struct.pack( "!HHIIHBx", source_port, dest_port, seqNum, ackNum, window, setASFbyte(ACK, SYN, FIN))

# unpack header information according to protocol design in README.md
def unpackHeader(header):
    source_port = struct.unpack('!H', header[0:2])[0]
    dest_port = struct.unpack('!H', header[2:4])[0]
    seqNum = struct.unpack('!I', header[4:8])[0]
    ackNum = struct.unpack('!I', header[8:12])[0]
    asfByte = struct.unpack('!B', header[14:15])[0]
    window = struct.unpack('!H', header[12:14])[0]
    ACK = int(format(asfByte, '08b')[0:1])
    SYN = int(format(asfByte, '08b')[1:2])
    FIN = int(format(asfByte, '08b')[2:3])
    return source_port, dest_port, seqNum, ackNum, window, ACK, SYN, FIN

def setASFbyte(ack=0,syn=0,fin=0):
    # convert int to string and conbine
    byte = str(ack)+str(syn)+str(fin)+('00000')
    return int(byte, 2)
