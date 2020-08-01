import socket
import select
import errno
import sys
from threading import Thread
from tkinter import *

firstclick = True


def on_entry_click(event):
    """function that gets called whenever entry1 is clicked"""
    global firstclick

    if firstclick: # if this is the first time they clicked it
        firstclick = False
        entry_field.delete(0, "end") # delete all the text in the entry



MAX_LENGTH = 10

IP = "127.0.0.1"
PORT  =1342


#create a socket on client side
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#establish connection to server
client_socket.connect((IP, PORT))
#set the recv method to not block
client_socket.setblocking(False)

#first thing we send to the server is user info
my_username = input("username: ")
username = my_username.encode('utf-8')
username_header = f"{len(username):<{MAX_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


def send_to_server(event=None):
    message = my_msg.get() #incase of sending a msg to the server
    my_msg.set("")  # Clears input field.

    if message == "{quit}":
        client_socket.close()
        root.quit()
    if message:
        #encode the message to utf-8
        message = message.encode('utf-8')
        #get the message_header and send both header ana original message
        message_header = f"{len(message):<{MAX_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)


def receive_from_server():
        #incase of receiving msgs from the server
    while True:
        try:
            #receive the username header
            username_header = client_socket.recv(MAX_LENGTH)

            #if we don't receive any data, connection is lost
            if not len(username_header):
                print('connection closed by the server')
                sys.exit()

            #get the length of username
            username_len = int(username_header.decode('utf-8').strip())
            #receive the actual username now
            username = client_socket.recv(username_len).decode('utf-8')

            #do the similar thing for the message
            message_header = client_socket.recv(MAX_LENGTH)
            message_len = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_len).decode('utf-8')

            #then print the message
            print(f"{username} > {message}")
            msg_list.insert(END, username + " : " + message)
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading error", str(e))
                sys.exit()
            continue #we didn't receive anything

        except Exception as e:# Any other exception - something happened, exit
            print("general error", str(e))
            sys.exit()




def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send_to_server()


root = Tk()
root.title("Chatroom")

messages_frame = Frame(root)
my_msg = StringVar()  # For the messages to be sent.
my_msg.set("Type here...")
scrollbar = Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, fill=BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = Entry(root, textvariable=my_msg)
entry_field.bind('<FocusIn>', on_entry_click)
entry_field.bind("<Return>", send_to_server)
entry_field.pack()
send_button = Button(root, text="Send", command=send_to_server)
send_button.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

receive_thread = Thread(target=receive_from_server)
#print('nnnnn')
receive_thread.start()
root.mainloop()

