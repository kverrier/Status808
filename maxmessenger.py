from socket import *

class MaxMessageSender:
    """
    Sends string messages to MAX/MSP through UDP socket.
    """
    def __init__(self, port=8085, bufsize=1024) :
        host = "localhost"
        port = port
        buf = bufsize
        self.addr = (host, port)

        self.UDPSock = socket(AF_INET,SOCK_DGRAM)

    def send_message(self, data):
        if(self.UDPSock.sendto(data,self.addr)):
            print "Sending message '",data,"'....."

    def __del__(self) :
        self.UDPSock.close()
