import socket, sys, time

def ip_header_constructor(sourceIP, destinationIP):
    # set ip

def main():

    # create raw socket
    try:
        # using raw IP Packets
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except socket.error:
        print ('Socket creation error')
        sys.exit()
    

if __name__ == "__main__":
    main()
