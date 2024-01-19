import threading
import sqlite3
import socket
import json
import sys

class GameClient:
    _instances = {}
    _instance_lock = threading.Lock()
    
    def __new__(cls, cookie_value=None):
        with cls._instance_lock:
            if cookie_value not in cls._instances:
                print(f"Creating a new GameClient instance for cookie: {cookie_value}")
                cls._instances[cookie_value] = super(GameClient, cls).__new__(cls)
                cls._instances[cookie_value]._initialized = False
                cls._instances[cookie_value].cookie_value = cookie_value
            return cls._instances[cookie_value]

    def __init__(self, cookie_value=None):
        with self._instance_lock:
            if self._initialized:
                return
            
            self._initialized = True
            self.logged_in = False
            self.server_address = ('localhost', 1423)
            self.socket = None
            self.user_id = ""
            self.token = -1
            self.socket_lock = threading.Lock()
            self.connected = False
            self.username = None
            self.load_token()
            self.cookie_value = cookie_value  # Store the cookie value
        
            self.socket_lock = threading.Lock()
            self.notification_thread_flag = threading.Event()

            while not self.connect():
                pass

            self.is_server_shutdown = False

    def connect(self):
        with self.socket_lock:
            if self.connected:
                return True

            if not self.socket:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.socket.connect(self.server_address)
                    self.connected = True
                    self.notification_thread = threading.Thread(target = self.receive_notification)
                    self.notification_thread.start()
                except ConnectionRefusedError:
                    print("Connection refused. Make sure the server is running.")
                    self.socket.close()
                    return False
            return True
        
    
    def table_exists(self, cursor, table_name):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None
        
    def save_token(self, user_id, token):
        with sqlite3.connect('client.sql3') as db:
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
         with sqlite3.connect('client.sql3') as db: 
            c = db.cursor()

            if self.table_exists(c, "tokens"):
                c.execute('SELECT user_id, token FROM tokens')
                row = c.fetchone()

                self.user_id = row[0]
                self.token = row[1]

    def close(self):
        with self.socket_lock:
            if self.socket:
                self.socket.close()
                del self.socket
                self.notification_thread_flag.set()
                self.notification_thread.join()

            self.connected = False

    def send_command(self, command):
        with self.socket_lock:
            self.socket.send(command.encode())
            response = json.loads(self.socket.recv(1024).decode())

            return response

    def register_user(self, username, fullname, email, password):
        command = {
            'command': 'R',
            'username': username,
            'fullname': fullname,
            'email': email,
            'password': password,
        }
        response = self.send_command(json.dumps(command))
        return response

    def login_user(self, username, password):
        command = {
            'command': 'L',
            'username': username,
            'password': password,
        }
        response = self.send_command(json.dumps(command))

        if response['Message'] == 'Logged in':
            self.logged_in = True
            self.user_id = response['user_id']  # Assuming the server sends the user_id upon successful login

        return response

    def logout_user(self):
        if not self.logged_in:
            return {'Message': 'Not logged in.'}
        command = {}
        command["command"] = "LO"
        command["user_id"] = self.user_id
        response = self.send_command(json.dumps(command))

        if response['Message'] == 'Logged out':
            self.logged_in = False
            self.user_id = None

        return response
    

    def query_map(self):
        command = {
            'command': "querymap",
            'user_id': self.user_id
        }

        return self.execute_command(command)

    def leave_map(self, map_id, teamname):
        command = {
            'command': "leavemap",
            'user_id': self.user_id,
            'map_id': map_id,
            'teamname': teamname
        }

        return self.execute_command(command)
    
    def join_map(self, map_id, teamname):
        command = {
            'command': "joinmap",
            'user_id': self.user_id,
            'map_id': map_id,
            'teamname': teamname
        }

        return self.execute_command(command)
    
    def drop_object(self, object):
        command = {
            'command': "drop",
            'user_id': self.user_id,
            'object_type': object
        }

        return self.execute_command(command)

    def move_player(self, direction):
        command = {
            'command': "move",
            'user_id': self.user_id,
            'direction': direction
        }

        return self.execute_command(command)
    
    def list_maps(self):
        command = {
            'command': "listmaps"
        }

        return self.execute_command(command)
    
    def new_map(self, name, size, type):
        command = {
            'command': "newmap",
            'map_name': name,
            'map_size': size,
            'config_template': type
        }

        response = self.execute_command(command)
        return response

    def execute_command(self, command):
        response = self.send_command(json.dumps(command))
        return response
    
    def receive_notification(self):
        while not self.notification_thread_flag.is_set():
            try:
                with self.socket_lock:
                    if (self.socket):
                        while True:
                            self.socket.settimeout(0.1)
                            data = json.loads(self.socket.recv(1024).decode())
                            if data:
                                break
                        if data["Message"] == "Server Shutdown":
                            server_shutdown_thread = threading.Thread(target=self.server_shutdown)
                            server_shutdown_thread.start()
                        else:
                            print("Data: ", data)

            except socket.timeout:
                pass
            finally:
                self.socket.settimeout(None)


    def server_shutdown(self):
        self.notification_thread_flag.set()
        self.notification_thread.join()

        print("\nServer has shutdown. Please exit with CTRL+C")
        command = {}
        command["command"] = "SS_Ack"
        self.send_command(json.dumps(command))

        with self.socket_lock:
            self.socket.close()

        sys.exit(0)

    def signal_handler(self, signal, frame):
        self.notification_thread_flag.set()
        self.notification_thread.join()

        print("\nReceived Ctrl+C. Closing connection...")
        command = {}
        command["command"] = "E"
        self.send_command(json.dumps(command))

        self.close()
        sys.exit(0)


def main():
    if len(sys.argv) != 3:
        print('usage: ', sys.argv[0], 'host port')
        sys.exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = GameClient(host, port)
    try:
        while True:
            command_str = input("Enter command: ")
            command = json.loads(command_str)

            if "command" in command:
                response = client.execute_command(command)

                if response["Message"] == "Logged in":
                    client.logged_in = True
                    client.user_id = response["user_id"]
                elif response["Message"] == "Logged out":
                    client.logged_in = False
                    client.user_id = None
                elif response["Message"] == "Server Shutdown":
                    client.server_shutdown()

                print(response["Message"])

    except json.JSONDecodeError:
        print("Invalid JSON format.")
    except KeyboardInterrupt:
        print("Received CTRL+C interrupt. Closing client...")
    except socket.error as e:
        print(f"Server disconnected unexpectedly: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
