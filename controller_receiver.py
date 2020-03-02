import socket

localIP     = "127.0.0.1"
localPort   = 12345
bufferSize  = 1024

s = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
s.bind((localIP, localPort))
#s.listen(10)

while True:
    #sensorsocket, address = s.accept()
    bytesAddressPair = s.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
	
    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

	#print(f"Connection from {address} has been established!")