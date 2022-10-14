import ssl
import socket

host = "10.5.0.204"
hostname = "minecraft-test.portalpcgaming.com"
port = 42047

sslContext = ssl.create_default_context()

print("Creating Socket on Port " + str(port) + ".")

try:
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Socket Created Successfully.")
except socket.error as err:
	print("Socket Creation Failed. Reason: " + err)
	
secureSock = sslContext.wrap_socket(clientSock, server_hostname=hostname)
	
secureSock.connect((host, port))
print("Connected to " + host + " on port " + str(port) + ".")

while True:
	data = input("Input data to send to " + host + ": \n")
	
	#mcSock.sendall(bytes(data, "UTF-8"))
	secureSock.sendall(data.encode("utf-8"))
