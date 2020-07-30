import socket
import select
import errno
import sys

MAX_LENGTH = 10

IP = "127.0.0.1"
PORT  =1342

my_username = input("username: ")
#create a socket on client side
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#establish connection to server
client_socket.connect((IP, PORT))
#set the recv method to not block
client_socket.setblocking(False)

#first thing we send to the server is user info
username = my_username.encode('utf-8')
username_header = f"{len(username):<{MAX_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


#a while loop for the actual process of a client
while True:
	message = input(f"{my_username} > ") #incase of sending a msg to the server

	if message:
		#encode the message to utf-8
		message = message.encode('utf-8')
		#get the message_header and send both header ana original message
		message_header = f"{len(message):<{MAX_LENGTH}}".encode('utf-8')
		client_socket.send(message_header + message)

	try:
		while True:
			username_header = client_socket.recv(MAX_LENGTH)

			if not len(username_header):
				print('connection closed by the server')
				sys.exit()
			username_len = int(username_header.decode('utf-8').strip())
			username = client_socket.recv(username_len).decode('utf-8')
			message_header = client_socket.recv(MAX_LENGTH)
			message_len = int(message_header.decode('utf-8').strip())
			message = client_socket.recv(message_len).decode('utf-8')
			print(f"{username} > {message}")
	except IOerror as e:
		if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
			print("Reading error", str(e))
			sys.exit()
		continue

	except Exception as e:
		print("general error", str(e))
		sys.exit()
