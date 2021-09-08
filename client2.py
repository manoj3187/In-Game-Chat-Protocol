# Filename: client.py
# written by: Manoj Venkatachalaiah

# Purpose: the file contains the code that connects a client to the server and
# caused it to validate the DFA. Upon succesful handshake steps, the 
#client will start sending messages to the server which will be forwarded to other clients.


#importing the necessarry libraries
import socket #for sending messages over sockets

#for handling multiple messages
import threading 


# definfing the client socket and connecting it to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# defining the Protocol version supported by the client
p_version=1

#defining user data, their usernames and player records
username="Conor"
p_rec= "Played: 201, Draw: 37, Won: 98, Lost: 66"



#this while loop is the beginning of the DFA validation on the CLient side    
while True:
        
    #the initial state of the DFA is set to idle    
    global p_state
    p_state = "idle"


    #when in idle state, the client sends a HOLA command to the and changes
    #the state to c_await
    if p_state == "idle":
        client.send('HOLA'.encode('ascii'))
        p_state = "c_awaits"
    else:
        client.close()
        print(p_state)
        print("409: In-Game Chat not available")
        break


    #when in the c_awaits state, the client expects to receive the 
    #protocol version from the server, upon receiving the VRSN command,
    #the state is changed to s_awaits. If not, a 409 error is thrown
    if p_state == 'c_awaits':

        message=client.recv(1024).decode('ascii')
        if message[0:4]=='VRSN':
                p_state = "s_awaits"
    else:
        client.close()
        print(p_state)
        print("409: In-Game Chat not available")        
        break
            
    #when in s_awaits, the client sends the version of the protocol it supports, and 
    # changes the state to c_awaits_tcag  
    if p_state == "s_awaits":
        client.send(f"VRSN-{p_version}".encode('ascii'))
        if p_version==1:
            p_state = "c_awaits_tcag"
        else:
            client.close()
            print(p_state)
            print("409: In-Game Chat not available")
            break

    #when in c_awaits_tcag state, the client receives the TCAG command and changes
    #the dfa state to s_awaits_tcag. Upon successful handshake, if the
    #TCAG command isn't received, the client throws a 409 error
    if p_state == "c_awaits_tcag":
        tac=client.recv(1024).decode('ascii')
        if tac == "TCAG":
            p_state = "s_awaits_tcag"
    else:
        client.close()
        p_state = "idle"
        print(p_state)
        print("409: In-Game Chat not available")
        break

    #when in  s_awaits_tcag, the client asks the user whether he/she
    # agrees to the terms and conditions. If a 'Y' is chosen by the user,
    # The client sends a TCS command to the server. If a "N" is chosen,
    # The cleint sends a TCN command to the server and tells the user that
    # the In-game chat isn't allowed. If an invalid response is entered
    # by the user, the client notifies the user and asks him/her to choose
    # a Y or an N. This will be repeated twice before the "In-game chat not 
    # allowed error is thrown.
    if p_state == "s_awaits_tcag":
        print("Do you agree to terms and conditions? Type Y or N and press enter")
        answer = input('')
        if answer == 'Y':
            client.send('TCS'.encode('ascii'))
            p_state="s_awaits_chat"
                
        elif answer=="N":
            client.send('TCN'.encode('ascii'))
            print("In-Game Chat not allowed")
            client.close()
            p_state = "idle"
            break
        else:
            print("Invalid answer, 2 attempts remaining, please type Y or N")
            p_state = 's_awaits_tcag'

    #invalid response iteration 2, clients tells user that two attemps are remaining
    if p_state == "s_awaits_tcag":
        print("Do you agree to terms and conditions? Type Y or N and press enter")
        answer = input('')
        if answer == 'Y':
            client.send('TCS'.encode('ascii'))
            p_state="s_awaits_chat"
                
        elif answer=="N":
            client.send('TCN'.encode('ascii'))
            print("In-Game Chat not allowed")
            client.close()
            p_state = "idle"
            break
        else:
            print("Invalid answer, 1 attempt remaining, please type Y or N")
            p_state = 's_awaits_tcag'

    #invalid response iteration 3, client tells user that one attempt is remaining  
    if p_state == "s_awaits_tcag":
        print("Do you agree to terms and conditions? Type Y or N and press enter")
        answer = input('')
        if answer == 'Y':
            client.send('TCS'.encode('ascii'))
            p_state="s_awaits_chat"
                
        elif answer=="N":
            client.send('TCN'.encode('ascii'))
            print("In-Game Chat not allowed")
            client.close()
            p_state = "idle"
            break
        else:
            print("In-Game Chat not allowed")
            p_state = 'idle'
            client.close()
            break

        
    print("Starting chat.")
    print("")
    print("""Please be respectful of your oponents and follow
    community rules and guidlines at all times""")
    print(".....")
    print("Enter text to send a message")
    print("Enter END to end chat.")
    print("Enter REPORT to report chat.")
    print(".....")
    break
    #handshaking and terms and conditions established


def write():
    #the write function enables the client to send messages to the server
    #the function takes an input from the UI and takes suitable action 
    # (described below)
    while True:
        try:
            enter_chat=input('')
            message = '{}: {}'.format(username, enter_chat)

            #if a user enters an END message, the command is sent to the server
            #which will be forwarded to all clients to let them know 
            #that the chat has ended. The chat will be ended when any of the users
            #send an end message
            if enter_chat == 'END':
                client.send('END'.encode('ascii'))
                client.close()
                print("Chat has ended")
                break

            #if a user enters an REPORT message, the command is sent to the server
            #which will cause the server to save chat history and forward the message
            #to all clients letting them know that the chat has been reported and that
            #they cannot continue chatting futher
            elif enter_chat == 'REPORT':
                client.send('RPRT'.encode('ascii'))
                client.close()
                print("Chat has been reported and will be examined by the administrative team.")
                print('Chat has ended')
                break
        
            #when the user inputs a normal chat message, it is sent to the server
            #so that it can be forwarded to all clients
            else:
                client.send(message.encode('ascii')) 
        except:
            break


def receive():
    #the receive function enables the client to recieve messages from
    #rhe server and take suitable actions
        while True:
            try:

                message = client.recv(1024).decode('ascii')
                #if the client receives an END command from the server,
                #incating that one of the other users wants to end the chat,
                #the client closes its connection and lets the user know the chat 
                #has ended
                if message == "END":
                    print("Your oponent has left the chat, press ENTER to quit.")
                    client.close()
                    break

                #if the client receives an RPRT command from the user,
                #indicating that the chat has been reported from the other
                #user, it closes the client connection and lets the user know
                # that the chat has been reported and that they cannot 
                # continue chatting  
                elif message == "RPRT":
                    print("Chat has been reported, you cannot continue chatting, press Enter to quit.")
                    client.close()
                    break

                #if the message isn't and END or REPORT, the client simoly
                #prints the message
                else:
                    print(message)

            #if the above block doesn't execute for some reason,
            #the client closes the connection
            except:
                client.close()
                break

if p_state =="s_awaits_chat":

#upon successful handshake and terms and conditions steps the threads
# for sending and receiving of messages to and from the server are started  
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()