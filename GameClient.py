import socket
import sys

# class to handle o allow for player/client functions
class PlayerClient:
    def __init__(self, serverIP, serverPort):
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.currentState = 4   # 0 : Out of House, 1: In the Game Hall, 2: Playing a Game, 3: Waiting in Room, #4: Exit

    # to update player states based on server resposnes
    def manage_response(self, response):
        if response == '4001 Bye bye':
            self.currentState = 4
        elif response == '1001 Authentication successful':
            self.currentState = 1
        elif response == '3011 Wait':
            self.currentState = 3
        elif response == '3012 Game Started. Please guess true or false':
            self.currentState = 2
        elif response == '3023 The result is a tie' or response == '3021 You are the winner' or response == '3022 You lost this game':
            self.currentState = 1

    #special case for authentication
    def authenticate(self):
        print("Please input your username")
        try:
            username = input()
        except:
            clientSocket.close()
            sys.exit(1)

        print("Please input your password")
        try:
            password = input()
        except:
            clientSocket.close()
            sys.exit(1)
        
        command = '/login ' + username + ' ' + password
        return command

    #main client loop for playing game
    def client_run(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((self.serverIP, self.serverPort))
        except socket.error as emsg:
            clientSocket.close()
            sys.exit(1)

        self.currentState = 0   # has connected to server and is Out of House

        while(self.currentState != 4):

            # waiting for response in case of waiting room
            if(self.currentState == 3):
                try:            
                    response = clientSocket.recv(1024)
                except socket.error as emsg:
                    clientSocket.close()
                    sys.exit(1)
                print(response.decode())
                self.manage_response(response.decode())

            # login state
            if(self.currentState == 0):
                command = self.authenticate()
            
            # Game Hall and Game Room states
            else:
                try:
                    command = input()
                except:
                    clientSocket.close()
                    sys.exit(1)

            try:
                clientSocket.send(command.encode())
            except socket.error as emsg:
                clientSocket.close()
                sys.exit(1)

            try:            
                response = clientSocket.recv(1024)
            except socket.error as emsg:
                clientSocket.close()
                sys.exit(1)

            print(response.decode())    #printing server response
            self.manage_response(response.decode())
            

        clientSocket.close()

if __name__  == '__main__':
    #checking for correct program input
    if len(sys.argv) != 3:
        print("Input Error")
        print("Usage: python3 GameClient.py <ServerIPAddress> <ServerPort>")
        sys.exit(1)
    
    serverIP = sys.argv[1]
    if not int(sys.argv[2]):
        print("Input Error: ServerPort to be of type integer")
        sys.exit(1)
    serverPort = int(sys.argv[2])

    playerClient = PlayerClient(serverIP, serverPort)
    playerClient.client_run()