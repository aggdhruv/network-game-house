# Network Based Game House Application

**Application Introduction** - The game house is a python application in which multiple clients connect to a game server, get authorized, and then select a game room to enter and play a game with another player in the same room.

  

This application was built as part of a Networks course assignment. Meant to explore network programming using python, and deal with abnormal test cases like incorrect messages, sudden client crashes, broken network connections and more.

  
  

**Running of Application**

  

1. Server Program -
- The server program takes 2 paramters: (1) server's listening port, (2) path to UserInfo.txt file containing usernames and passwords of clients
- Run as: `python3 GameServer.py <server_port> <path_to_UserInfo.txt>`

2. Client Program -
- The client program takes 2 parameters: (1) hostname or IP address of the server; (2) listening port of the server.
- Run as: `python3 GameClient.py <server_ip_address> <server_port>`

  
  

**Client Side Commands**

  

1.  *Authentication* - enter username and password on prompt. On successful login, client will be in the Game Hall

  

2.  *In the Game Hall* -

  

-  `/list`: will list No of rooms and availability, and no of users in each room

  

-  `/enter <room_number>`: depending on availability will allow you to enter room `<room_number>`

  

-  `/exit`: will allow you to exit game hall and exit application

- To play the simple game, a room requires 2 clients to join. If there is already a client in the room, then user will join Game Room and the simple game will immediately start. If there is no one in the room, the user will wait till another client joins.

  

3.  *In the Game Room* - The game to be played is a simple game of chance. The 2 clients enter `true` or `false` when prompted. Command should be `/guess <input>`.

  

- if both inputs are equal, the result is a tie

  

- if not the computer generates a guess, and the client with the matching guess wins.

- Both clients automatically return to the game hall on finishing the game

  

**Certain Assumptions Made (Part of Requirements)-**

  

1. User can only `/exit` the application when in the game hall, and not while waiting or playing the game

  

2. A particular user doesn't log in from two terminals simultaneously

  

3. The clients will keep running and would need to be closed manually in case the server crashes unexpectedly

  

4. If a User A exits the game while 2 users are in the game room, and if the other Player B has already played a move or plays a move after the user exits, then Player B is automatically declared the winner. But in case, User A has left and Player B has not played a move, then Player B would not be automatically declared a winner if another third Player C joins the room before Player B plays a move. The game in that scenario continues as before.