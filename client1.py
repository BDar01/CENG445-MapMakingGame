import socket
import signal
import sys
import json
import sqlite3
import threading

from singleton import UserFactory, MapFactory

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

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
            sys.exit(0)
        # Register the signal handler for CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)
        self.user_id = ""
        self.token = -1
        self.load_token()

        self.socket_lock = threading.Lock()
        self.notification_thread_flag = threading.Event()

        self.notification_thread = threading.Thread(target = self.receive_notification)
        self.notification_thread.start()

        self.is_server_shutdown = False

    def save_token(self, user_id, token):
        with sqlite3.connect('client1.sql3') as db:
            c = db.cursor()

            try:
                c.execute('''
                    DROP TABLE IF EXISTS tokens 
                ''')
                c.execute('''
                    CREATE TABLE tokens (
                        user_id TEXT PRIMARY KEY NULL,
                        token TEXT NOT NULL
                    )
                ''')

                c.execute("INSERT INTO tokens (user_id, token) VALUES (?, ?)", (user_id, token))
                db.commit()

            except sqlite3.Error as e:
                print(f"Error executing SQL query: {e}")

    def load_token(self):
         with sqlite3.connect('client1.sql3') as db: 
            c = db.cursor()

            if table_exists(c, "tokens"):
                c.execute('SELECT user_id, token FROM tokens')
                row = c.fetchone()

                self.user_id = row[0]
                self.token = row[1]


    def print_notification(self, notification):
        sender_username = notification["Sender"]
        message = notification["Body"]
        print(f"\nNotification from '{sender_username}':  {message}\n")

    def send_command(self, command):
        with self.socket_lock:
            flag = True
            while flag:
                self.client_socket.send(command.encode())
                response = json.loads(self.client_socket.recv(1024).decode())
                if response['Message'] == "Notification":
                    self.print_notification(response)
                else:
                    flag = False
        return response

    def receive_notification(self):
        while not self.notification_thread_flag.is_set():
            try:
                with self.socket_lock:
                    while True:
                        self.client_socket.settimeout(0.1)
                        data = json.loads(self.client_socket.recv(1024).decode())
                        if data:
                            break
                    if data["Message"] == "Server Shutdown":
                        server_shutdown_thread = threading.Thread(target=self.server_shutdown)
                        server_shutdown_thread.start()
                    else:
                        self.print_notification(data)

            except socket.timeout:
                pass
            finally:
                self.client_socket.settimeout(None)

    def close(self):
        self.client_socket.close()

    def server_shutdown(self):
        self.notification_thread_flag.set()
        self.notification_thread.join()
        self.is_server_shutdown = True

        print("\nServer has shutdown. Please exit with CTRL+C")
        command = {}
        command["command"] = "SS_Ack"
        self.send_command(json.dumps(command))

        with self.socket_lock:        
            self.client_socket.close()

        sys.exit(0)


    def signal_handler(self, signal, frame):
        self.notification_thread_flag.set()
        self.notification_thread.join()

        print("\nReceived Ctrl+C. Closing connection...")
        command = {}
        command["command"] = "E"
        self.send_command(json.dumps(command))

        with self.socket_lock:        
            self.client_socket.close()

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
        if client.token != -1:
            response = client.send_command(json.dumps({'command': "C", 'user_id': client.user_id, 'token': client.token }))
            if response["Message"] == "Logged in":
                client.logged_in = True
                print(response["Message"])
            else:
                client.token = -1

        while not client.is_server_shutdown:
            command = {}
            if not client.logged_in:
                user_input = input("Register(R), Login(L) and Exit(E): ")
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
                    pass

                response = client.send_command(json.dumps(command))

                print(response["Message"])

                if response['Message'] == "Logged in":
                    client.logged_in = True
                    client.token = response['token']
                    client.user_id = response['user_id']
                    client.save_token(client.user_id, client.token)

                elif response['Message'] == "Exit":
                    break

                elif response['Message'] == "Username exists. Please try for another username.":
                    continue
                

            else:
                user_input = input("Enter a command (Logout (LO) or Exit(E)): ")
                response = ""
                
                if user_input == "E":
                    command["command"] = user_input
                    response = client.send_command(json.dumps(command))
                    print(response["Message"])
                    

                elif user_input == "LO":
                    command["command"] = user_input
                    command["user_id"] = client.user_id
                    response = client.send_command(json.dumps(command))
                    print(response["Message"])


                elif user_input.find("newmap") != -1:
                    c = user_input.split()
                    if len(c) == 4:
                        command["command"], command["map_name"], command["map_size"], command["config_template"] = c[0], c[1], c[2], c[3] 
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])

                    else:
                        print("Invalid argument count. Try again.")

                elif user_input.find("joinmap") != -1:
                    c = user_input.split()
                    if len(c) == 3:
                        command["command"], command["user_id"], command["map_id"], command["teamname"] = c[0], client.user_id, c[1], c[2] 
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])

                    else:
                        print("Invalid argument count. Try again.")

                elif user_input.find("leavemap") != -1:
                    c = user_input.split()
                    if len(c) == 3:
                        command["command"], command["user_id"], command["map_id"], command["teamname"] = c[0], client.user_id, c[1], c[2] 
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])

                    else:
                        print("Invalid argument count. Try again.")

                elif user_input.find("listusers") != -1:
                    c = user_input.split()

                    if len(c) == 1:
                        command["command"] = c[0]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    else:
                        print("No arguments required for this command. Please try again.")

                elif user_input.find("listmaps") != -1:
                    c = user_input.split()

                    if len(c) == 1:
                        command["command"] = c[0]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    else:
                        print("No arguments required for this command. Please try again.")

                elif user_input.find("querymap") != -1:
                    c = user_input.split()
                    if len(c) == 4:
                        command["command"], command["user_id"], command["x"], command["y"], command["radius"] = c[0], client.user_id, c[1], c[2], c[3]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    elif len(c) == 2:
                        command["command"], command["user_id"], command["radius"] = c[0], client.user_id, c[1]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    elif len(c) == 1:
                        command["command"], command["user_id"] = c[0], client.user_id
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    else:
                        print("Invalid argument count. Try again.")
                
                elif user_input.find("move") != -1:
                    c = user_input.split()

                    if len(c) == 2:
                        command["command"], command["user_id"], command["direction"] = c[0], client.user_id, c[1]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    
                    else: 
                        print("Invalid number of arguments. Try again.")

                elif user_input.find("drop") != -1:
                    c = user_input.split()

                    if len(c) == 2:
                        command["command"], command["user_id"], command["object_type"] = c[0], client.user_id, c[1]
                        response = client.send_command(json.dumps(command))
                        print(response["Message"])
                    else:
                        print("Invalid number of arguments. Try again.")

                else:
                    c = user_input.split()
                    command["command"] = c[0]
                    response = client.send_command(json.dumps(command))
                    print(response["Message"])

                if response:
                    if response["Message"] == "Logged out":
                        client.token = -1
                        client.logged_in = False
                        
                    elif response["Message"] == "Exit":
                        break
    
    except json.JSONDecodeError:
        # Handle the case where the response is not a JSON object (e.g., a string)
        print("JSON Decode Error occured.")
        # Handle the response accordingly, e.g., print or log it
    except KeyboardInterrupt:
        print("Received CTRL+C interrupt. Closing client...")
        pass
    except socket.error as e:
        print("Server disconnected unexpectedly.")
        pass
    finally:
        if not client.notification_thread_flag.is_set():
            client.notification_thread_flag.set()
        client.close()
