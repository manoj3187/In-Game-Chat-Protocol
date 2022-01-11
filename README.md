• The IGC protocol is a prototype built to facilitate in-game and respectful text chatting between players of games
such as FIFA 22 and 2K22.

• The IGC protocol operates over TCP/IP and hosts a server that’s listens to incoming connections over a socket- a designated IP address (127.0.0.1) and port number (55555). The server then completes a connection to a client after a series of initialization and handshaking procedures via exchange of messages. Suitable custom error codes/messages are thrown in case of a failure (400, 409, TCN, server_awaits etc)

• Multithreading is used to allow more than 100 client connections to the server. A routing table is used to keep track of all the clients and their destination IP addresses in order to route the incoming and outgoing ascii encoded text messages among clients, thereby simulating a chat.
