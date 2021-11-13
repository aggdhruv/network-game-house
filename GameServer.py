import socket
import sys
import threading
import random

#class for player thread and controls all server actions for individual player
class PlayerThread(threading.Thread):
    room_generated_guess = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: []}  # static variable across PlayerThread instances to store guesses in game
    rooms_filled = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: []}  # static variable across PlayerThread instances to store threads in each individual room
    def __init__(self, client, userLoginInfo):
        threading.Thread.__init__(self)
        self.client = client
        self.userLoginInfo = userLoginInfo
        self.lock = threading.Lock()
        self.rooms = 10
        self.currentRoom = -1
        self.currentState = 0   # 0 : Out of House, 1: In the Game Hall, 2: Playing a Game, 3: Waiting in Room, #4: Exit
        self.messages = {1001 : '1001 Authentication successful',
                        1002 : '1002 Authentication Failed',
                        3001 : f'3001  {self.rooms} ',
                        3011: '3011 Wait',
                        3012: '3012 Game Started. Please guess true or false',
                        3013: '3013 The room is full',
                        3023: '3023 The result is a tie',
                        3021: '3021 You are the winner',
                        3022: '3022 You lost this game',
                        4001: '4001 Bye bye',
                        4002: '4002 Unrecognized message'}   
    
    # to handle user authentication for player
    def login(self, message):
        messageParts = message.split()
        if len(messageParts) != 3 or messageParts[0]!= '/login':
            return self.messages[4002]
        if messageParts[1] in self.userLoginInfo and self.userLoginInfo[messageParts[1]] == messageParts[2]:
            self.currentState = 1
            return self.messages[1001]
        else:
            return self.messages[1002]

    # to handle client commands while in Game Hall
    def game_hall(self, message):
        messageParts = message.split()

        if(len(messageParts) == 1):
            if(messageParts[0] == '/list'):
                temp_l = [len(self.rooms_filled[i]) for i in self.rooms_filled]
                temp_l = map(str,temp_l)
                return self.messages[3001] + ' '.join(temp_l)
            elif(messageParts[0] == '/exit'):
                self.currentState = 4
                return self.messages[4001]
            else:
                return self.messages[4002]
        
        elif(len(messageParts)==2 and messageParts[0]=='/enter'):
            if(int(messageParts[1]) and int(messageParts[1])>=1 and int(messageParts[1])<10):
                room_num = int(messageParts[1])
                if(len(self.rooms_filled[room_num]) == 2): #room full
                    return self.messages[3013]
                elif(len(self.rooms_filled[room_num]) == 0): #room empty
                    self.currentState = 3
                    self.lock.acquire() #for safe editing and access of static variable rooms_filled common to threads
                    self.rooms_filled[room_num].append(self)
                    self.room_generated_guess[room_num].clear() #to remove old values of guesses
                    server_guess = random.choice(['true', 'false'])    # generate server guess for room
                    self.room_generated_guess[room_num].append(server_guess)
                    self.lock.release()
                    self.currentRoom = room_num
                    return self.messages[3011]
                else:   # exisitng player in room
                    self.currentState = 2
                    self.lock.acquire()
                    self.rooms_filled[room_num].append(self)
                    self.lock.release()
                    self.currentRoom = room_num
                    return self.messages[3012]
            else:
                return self.messages[4002]

        else:
            return self.messages[4002]
        
    #to implement Waiting Room function
    def waiting_room(self):
        while(True):
            # run loop till another user joins room and is ready to play
            if(len(self.rooms_filled[self.currentRoom]) == 2):
                self.currentState = 2
                return self.messages[3012]

    #to process game based on player guess
    def game_processing(self):
        while(True):
            if(len(self.room_generated_guess[self.currentRoom])==3):
                if self.room_generated_guess[self.currentRoom][1] == self.room_generated_guess[self.currentRoom][2]:
                    return self.messages[3023]
                else:
                    if(self.guess == self.room_generated_guess[self.currentRoom][0]):
                        return self.messages[3021]
                    else:
                        return self.messages[3022]
            if(len(self.rooms_filled[self.currentRoom]) !=2):   #in case other player abruptly leaves
                return self.messages[3021]

    # to implement game room
    def game_room(self, message):
        messageParts = message.split()
        if(len(messageParts) !=2 or messageParts[0]!= '/guess'):
            return self.messages[4002]
        
        if(messageParts[1] == 'true' or messageParts[1]=='false'):
            # storing player guess
            self.lock.acquire()
            self.room_generated_guess[self.currentRoom].append(messageParts[1])
            self.lock.release()
            self.guess = messageParts[1]
            response = self.game_processing()
            
            #returning state to Game Hall
            self.currentState = 1
            self.lock.acquire()
            self.rooms_filled[self.currentRoom].remove(self)
            self.lock.release()
            self.currentRoom = -1
            return response
        else:
            return self.messages[4002]

    #main server thread loop for player
    def run(self):
        connectionSocket, addr = self.client

        while(self.currentState != 4):

            # case when player is in waiting room
            if(self.currentState == 3):
                response = self.waiting_room()
                connectionSocket.send(response.encode())

            try:
                playerCommand = connectionSocket.recv(1024)
            except socket.error as emsg:
                print('Socket receiving error: ' + emsg)
                sys.exit(1)

            if playerCommand:
                message = playerCommand.decode()
                if(self.currentState == 0):
                    response = self.login(message)

                elif(self.currentState == 1):
                    response = self.game_hall(message)

                elif(self.currentState == 2):
                    response = self.game_room(message)

                connectionSocket.send(response.encode())
            else:
                print('Connection is broken')
                #in case client abruplty leaves
                self.lock.acquire()
                if(self.currentRoom != -1):
                    self.rooms_filled[self.currentRoom].remove(self)
                    self.currentRoom = -1
                self.lock.release()
                connectionSocket.close()
                sys.exit(1)

        connectionSocket.close()

#class to run main server and generate player threads
class MainServer:
    def __init__(self, serverPort, userLoginInfo):
        self.serverPort = serverPort
        self.userLoginInfo = userLoginInfo

    def server_run(self):
        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.bind(('', self.serverPort))
        except socket.error as emsg:
            print("Socket error: " + emsg)
            sys.exit(1)

        serverSocket.listen(10)
        print("The server is ready to receive")

        while True:
            try:
                client = serverSocket.accept()
            except socket.error as emsg:
                print('Socket accept message error: ' + emsg)
                sys.exit(1)
            player = PlayerThread(client, self.userLoginInfo)
            player.start()



if __name__ == '__main__':
    #checking for correct program input
    if len(sys.argv) != 3:
        print("Input Error")
        print("Usage: python3 GameServer.py <ServerPort> <UserInfo_File_Path>")
        sys.exit(1)
    
    #checking for valid serverPort
    if not int(sys.argv[1]):
        print("Input Error: ServerPort to be of type integer")
        sys.exit(1)
    serverPort = int(sys.argv[1])

    #logging username and password information for users
    userLoginInfo = dict({})
    userInfoPath = sys.argv[2]
    try:
        userInfoFileStream = open(userInfoPath, 'r')
    except OSError as emsg:
        print('File open error: ' + emsg)
        sys.exit(1)
    userInfoFile = userInfoFileStream.read().split()
    for userInfo in userInfoFile:
        username, password = userInfo.split(':')
        userLoginInfo[username] = password

    mainServer = MainServer(serverPort, userLoginInfo)
    mainServer.server_run()

