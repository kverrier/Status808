from socket import *

host = "localhost"
port = 8085
buf = 1024
addr = (host, port)

UDPSock = socket(AF_INET,SOCK_DGRAM)

def_msg = "===Enter message to send to server===";
print "\n",def_msg

while (1):
    data = raw_input('>> ')
    if not data:
        break
    else:
        if(UDPSock.sendto(data,addr)):
            print "Sending message '",data,"'....."

# Close socket
UDPSock.close()
