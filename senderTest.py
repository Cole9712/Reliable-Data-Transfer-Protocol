import socket, struct, sys, time


def main():
     # Define Server IP Address and Port
    serverName = 'localhost'
    serverPort = 6666
    # Build Server Address Using IP Address and Port
    serverAddress=(serverName, serverPort)
    
    # Create UDP Socket for Client
    clientSocket = socket.socket( socket.AF_INET, socket.SOCK_RAW )
    packet = struct.pack("iiii", 12, 23, 34, 45 )
    
    clientSocket.sendto(packet, serverAddress ) # AF_INET address must be tuple, not str
	# Both LISTS and TUPLES consist of a number of objects
    
    clientSocket.close()
    



if __name__ == "__main__":
    main()
