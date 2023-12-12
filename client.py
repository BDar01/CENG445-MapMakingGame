import socket
import signal
import sys
import json

from singleton import UserFactory, MapFactory

class GameClient:
    def __init__(self, host, port):
        self.logged_in = False
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))  # Replace with the server's IP address and port
        except ConnectionRefusedError:
            print("Connection refused. Make sure the server is running.")
            self.client_socket.close()
        # Register the signal handler for CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)
        self.user = None

    def send_command(self, command):
        self.client_socket.send(command.encode())
        response = self.client_socket.recv(1024).decode()
        return response

    def close(self):
        self.client_socket.close()

    def signal_handler(self, signal, frame):
        print("Received Ctrl+C. Closing connection...")
        self.close()
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ', sys.argv[0], 'host port')
        sys.exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = GameClient(host, port)
    try:
        peername = client.client_socket.getpeername()
        print(f"Connected to {peername}.")
        while True:
            if not client.logged_in:
                print("here")
                command = {}
                user_input = input("Register(R), Login(L) or Exit(E): ")
                command["command"] = user_input
                if user_input == "R":
                    username = input("Username: ")
                    fullname = input("Full Name: ")
                    email = input("Email: ")
                    password = input("Password: ")

                    command["username"] = username
                    command["fullname"] = fullname 
                    command["email"] = email
                    command["password"] =  password

                elif user_input == "L":
                    username = input("Username: ")
                    password = input("Password: ")

                    command["username"] = username
                    command["password"] =  password

                elif user_input == "E":
                    break
                response = client.send_command(json.dumps(command))
                print(response)
                if response == "OK":
                    client.logged_in = True
                elif response == "User added successfully. Please login.":
                    client.user = UserFactory().new(username, email, fullname, password)
                    print(UserFactory().user_list.items())
            else:
                user_input = input("Enter a command (Exit(E)): ")
                if user_input == "E":
                    break
                else:
                    print(UserFactory().user_list.items())
                    response = client.send_command(user_input)
                    print(response)

    except KeyboardInterrupt:
        pass
    except socket.error as e:
        pass
    finally:
        client.close()
