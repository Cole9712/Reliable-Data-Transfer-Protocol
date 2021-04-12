import struct

# pack header into binary string
def makeHeader( src, dest, seqN, ackN, window, asf ) -> bytes:
    return struct.pack( "!HHIIHBx", src, dest, seqN, ackN, window, asf )


# receive specific elements from the header
def getHeader( header, src = False, dest = False, seqN = False, ackN = False,
        window = False, ack = False, syn = False, fin = False ) -> tuple:
    hsrc, hdest, hseqN, hackN, hwindow, hasf = struct.unpack( "!HHIIHBx", header )
    hack = format( hasf, '08b' )[0]
    hsyn = format( hasf, '08b' )[1]
    hfin = format( hasf, '08b' )[2]

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
    src, dest, seqN, ackN, window = struct.unpack( "!HHIIH", prev )
    seqN = newSeqN if newSeqN != 0 else seqN + 1
    ackN = newAckN if newAckN != 0 else ackN
    window = newWindow if newWindow != 0 else window
    asf = int( asf + "00000", 2 )
    return makeHeader( src, dest, seqN, ackN, window, asf )
