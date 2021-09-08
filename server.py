# Filename: server.py
# written by: Manoj Venkatachalaiah

# Purpose: the file starts the server and accepts multiple clients so 
# they can chat with eachother. The code starts off by having the 
# server validate each state of the DFA and throwing suitable error
#  messages. Upon successful handshake between client and the server, 
# the server starts to act as a forwarding agent between the clients. 
# The server ends the chat when one of the clients send an END message 
# and stores the chat when a REPORT message is sent.


#importing the necessarry libraries
import socket #for sending messages over sockets
import threading #for handling multiple clinets
import pickle #for storing chat history

#defining the server ip address and port number required for clients to
# connect to the server
host = '127.0.0.1'
port = 55555



# Starting Server and binding it to the ip address and port number
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

#server listens to incoming connections
server.listen()
print("Server listening to incoming connections")

#defining the version of the IGC protocol
p_version=1

#keeping track of all connected clients and their usernames
clients = []
usernames =[]

def broadcast(message,c):
    #the brodcast function forwards the messages to all clients except 
    # the sending client
    for client in clients:
        if client!=c:
            client.send(message)

def broadcast_end(message):
    #the brodcast_end function forwards the messages to all clients  

    for client in clients:
        client.send(message)

#Initializing  a list to save chat history
chat_history=[]

def handle(client):
    #the handle function handles an incoming message from a client
    # and forwards it to other clients
    while True:
        try:
            message = client.recv(1024)

            #if the server receives an END message from one of the clients
            #it forwards the END message to all clients
            if message.decode('ascii') == "END":
                broadcast_end("END".encode('ascii'))
                print('Server closing...')
                print("Chat history:")
                print(chat_history)
                break
            #if the server receives an END message from one of the clients
            #it forwards the END message to all clients and saves the 
            #chat history which will be examined by the administrative team
            elif message.decode('ascii') == "RPRT":
                broadcast_end("RPRT".encode('ascii'))
                print("Saving chat history:")
                with open('chat_history.pkl', 'wb') as f:
                    pickle.dump(chat_history, f)   #saving chat history             
                print(chat_history)
                print('Server closing...')

                break

            #if the server receives a normal chat message, it appends the 
            # message to chat_history list and forwards it to everyother
            # client but the sending client
            else:
                chat_history.append(message.decode('ascii'))
                broadcast(message,client)
        except:
            # Incase of an error, clients are removed and connections are 
            #closed
            clients.remove(client)
            client.close()
            break

def close(client):
    #the function close(client) closes the connection to a particular client
    client.close()

def server_dfa():
    #this is the beginning of the server DFA validation, the intial state of 
    #the dfa is set to idle. The protocol state keeps changing upon
    #successful state validations, if not, suitable error messages are thrown
    while True:
        
        #server accepts incoming clients and appends it to client list
        client, address  = server.accept()
        clients.append(client)
        print("....")
        print("Server log:")

        #the initial state of the dfa
        global p_state
        p_state = "idle"
        
        print(f"Protocol state: {p_state}")




        #when a client connects, it sends a HOLA message which causes the state
        #to change to c_awits. If a HOLA message isn't sent, the server throws error 409
        if p_state=="idle":
            message=client.recv(1024).decode('ascii')
            if message=='HOLA':
                p_state = "c_awaits"
        else:
            close(client)
            print("409: In-Game Chat not available")
            p_state = "idle"
        
        print(f"Protocol state: {p_state}") #current state is printed

        #the server then sends the highest version it supports to the 
        #client through a VRSN-n command and changes the state to s_awaits
        if p_state == "c_awaits":
            client.send(f"VRSN-{p_version}".encode('ascii'))
            p_state = "s_awaits"
        else:
            close(client)
            print("409: In-Game Chat not available")
            p_state = "idle"

        print(f"Protocol state: {p_state}") #current state is printed
        
            
        #when in s_awaits, the server expects the client to send the protocol
        #version the client supports. It verifies that the version number returned 
        #by the client is less than or equal to the version it supports
        #Upon successful handshake, it changes the state to c_awaits_tcag, if
        #not it throws an error message
        if p_state == "s_awaits":
            ver=client.recv(1024).decode('ascii')
            if int(ver[-1])<=p_version:
                p_state = "c_awaits_tcag"
        else:
            print("409: In-Game Chat not available")
            close(client)
            p_state = "idle"

        print(f"Protocol state: {p_state}")
        
            
        #when in c_awaits_tcag state the server sends the TCAG, command to
        #the clients asking them to agree to the terms and conditions.
        #the clients will be allowed to chat only if both clients agree to 
        #the terms and conditions
        if p_state == "c_awaits_tcag":
            client.send("TCAG".encode('ascii'))
            p_state="s_awaits_tcag"
        else:
            print("409: In-Game Chat not available")
            close(client)
            p_state = "idle"

        print(f"Protocol state: {p_state}")
            
        #when in s_awaits_tcag state, the server expects to receive
        #either a TCS or a TCN from the clients. Clients will be allowed 
        #to chat only if they send a TCS command. If they send a TCN,
        #the server lets them know that they aren't allowed to chat
        if p_state == "s_awaits_tcag":
            answer = client.recv(1024).decode('ascii')
            if answer == "TCS":
                p_state = "s_awaits_chat"

            elif answer == "TCN":
                close(client)
                print("In-game chat not allowed ")
                p_state='idle'
        
        #final state of the protocol before start of chat, if the previous 
        # handshaking steps and terms and condition steps have been successful
        #the state should be s_awaits_chat
        print(f"Protocol state: {p_state}") 


        #this is the thread that enables the server to handle multiple
        #clients at once, the client starts forwarding the messages to clients
        thread = threading.Thread(target=handle,args=(client,))
        thread.start()


#finally, the server_dfa function is called to get the server running, 
#listening to clients, validating the dfa and forwarding messages between
# clients
server_dfa()

