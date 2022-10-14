import ssl
import MCUtil
import socket
import logging

HOST = "10.5.0.204"
PORT = 42047
flag = True
bufferSize = 2048

utility = MCUtil.MCUtil()

print("Creating Socket on Port " + str(PORT) + ".")

#Attempts to create a socket for IPv4 communication.
try:
	servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("CREATED: Socket Created Successfully.")
except socket.error as err:
	print("FAILURE: Socket Creation Failed. Reason: " + err)

#Attempts to create the SSL context wrapper to wrap the socket previously created	
try:
	sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	sslContext.load_cert_chain("STAR_portalpcgaming_com.pem", "portalpcgaming_prv.key")
	print("CREATED: SSL Context created to wrap socket")
except:
	print("FAILURE: Can't create secure context. \n")
	
#Binds the socket to the desired port.	
servSock.bind((HOST, PORT))
print("BOUND: Socket Bound to Port " + str(PORT) + ".")

#Begins listening on the socket created.
servSock.listen()
print("LISTENING: Now Listening on Port " + str(PORT) + ".")

#Attempts to wrap the socket in the SSL context creating a secure socket connection.
try:
	secureSock = sslContext.wrap_socket(servSock, server_side=True)
	print("WRAPPED: Socket wrapped in SSL context.")
except:
	print("FAILURE: Couldn't wrap socket in SSL context. Check configuration.")
	
#Creates the connection and parses connection metadata	
conn, addr = secureSock.accept()
print("CONNECTION ACCPETED: Connected with " + str(addr) + ".")

while flag == True:	
	#Receives the data from the client and saves it to the data variable to be compared to the list of acceptable commands.
	data = conn.recv(bufferSize)
	
	if not data:
		flag = False
	elif data.decode("utf-8") == "install":
		utility.install()

	elif data.decode("utf-8") == "setConfiguration":
		#SECOND ARGUMENT: Option within mc_utility.info to change.
		#THIRD ARGUMENT: The value for the option that you're trying to change.
		utility.setConfiguration(sys.argv[2], sys.argv[3])
		
	elif data.decode("utf-8") == "listConfiguration":
		utility.listConfiguration()

	elif data.decode("utf-8") == "backup":
		utility.backupServer()
		
	elif data.decode("utf-8") == "update":
		utility.update()
		
	elif data.decode("utf-8") == "remove":
		utility.remove()
		
	#elif data.decode("utf-8") == "dlbackup":
		#SECOND ARGUMENT: Location to place ZIP backup.
		#THIRD ARGUMENT: IP/Domain of where the backup is located.

	elif data.decode("utf-8") == "unpack":
		#SECOND ARGUMENT: Where to unpack the server files to
		#THIRD ARGUMENT: ZIP file to unpack into current environment
		utility.unpackServer(sys.argv[2], sys.argv[3])

	elif data.decode("utf-8") == "listServerProperties":
		utility.listServerProperties()
			
	elif data.decode("utf-8") == "changeServerProperties":
		#SECOND ARGUMENT: A property within the server.properties file.
		#THIRD ARGUMENT: The value which will be set for the specified property.
		utility.changeServerProperties()