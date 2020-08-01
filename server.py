import socket
import select 

MAX_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

#setup the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#this modifies the socket to allow us to reuse the address.
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#connect to given IP and PORT
server_socket.bind((IP, PORT)) 
server_socket.listen()

#list of sockets 
sockets_list = [server_socket]
#dictionary for clients(list of users)
clients = {}


print(f'Listen for connections on {IP}:{PORT}...')
#This function handles message receiving
def receive_msg(client_socket):
	try:
		message_header = client_socket.recv(MAX_LENGTH) #read the header

		if not len(message_header): #when a client closes connection
			return False
		#convert header to a length and return dictionary
		message_len = int(message_header.decode('utf-8').strip())
		return {"header": message_header, "data": client_socket.recv(message_len)}

	except:
		return False

#a while loop for the whole process of connecting and taking meassages from clients
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) #read lits, write list and error list

   
    for notified_socket in read_sockets: #read_sockets are sockets that have data to be read.
    	if notified_socket == server_socket: #incase of new connection
    		client_socket, client_addr = server_socket.accept() #connection established
    		user = receive_msg(client_socket) #getting the user info

    		if user is False:
    			continue

    		sockets_list.append(client_socket) #append to the sockets_list
    		clients[client_socket] = user #save the user info
    		print(f"Accepted new connection from {client_addr[0]}:{client_addr[1]}, username:{user['data'].decode('utf-8')}")

    	else: #in case of a new message from an existing client
    		message = receive_msg(notified_socket) #get the message info

    		if message is False: #This means connection is closed with the client
    		    print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
    		    # Remove from list for socket.socket()
    		    sockets_list.remove(notifed_socket) 
    		    # Remove from our list of users
    		    del clients[notified_socket]
    		    continue

    		user = clients[notified_socket]
    		print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

    		for client_socket in clients: # send the above message to the remaining clients
    		    #if client_socket != notified_socket: #exclude the client which sent the msg
    		        #sending both user header and data from clients dict. Message header and data which we received just now
    		    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])


    # handle some socket exceptions
    for notified_socket in exception_sockets:
    	# Remove from list for socket.socket()
    	sockets_list.remove(notified_socket)
    	# Remove from our list of users
    	del clients[notified_socket]
                    

