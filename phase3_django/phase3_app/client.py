import threading
import sqlite3
import socket
import json
import sys

class GameClient:
    _session_sockets = {}  # Global dictionary to store client sockets

    def __init__(self, host, port, session_key):
        self.logged_in = False
        self.server_address = (host, port)
        self.session_key = session_key
        self.user_id = ""
        self.token = -1
        self.socket_lock = threading.Lock()
        self.connected = False
        self.load_token()

        self.socket_lock = threading.Lock()
        self.notification_thread_flag = threading.Event()

        self.notification_thread = threading.Thread(target = self.receive_notification)
        self.notification_thread.start()

        self.is_server_shutdown = False
        
        self.connect()

    def connect(self):
        with self.socket_lock:
            if self.connected:
                return True

            if self.session_key not in self._session_sockets:
                self._session_sockets[self.session_key] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self._session_sockets[self.session_key].connect(self.server_address)
                    self.connected = True
                except ConnectionRefusedError:
                    print("Connection refused. Make sure the server is running.")
                    self._session_sockets[self.session_key].close()
                    del self._session_sockets[self.session_key]
                    return False
            return True
        
    def table_exists(self, cursor, table_name):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None
        
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

            if self.table_exists(c, "tokens"):
                c.execute('SELECT user_id, token FROM tokens')
                row = c.fetchone()

                self.user_id = row[0]
                self.token = row[1]

    def close(self):
        with self.socket_lock:
            if self.session_key in self._session_sockets:
                self._session_sockets[self.session_key].close()
                del self._session_sockets[self.session_key]
                self.connected = False

    def send_command(self, command):
        with self.socket_lock:
            if not self.connect():
                return {'Message': 'Server connection failed.'}

            self._session_sockets[self.session_key].send(command.encode())
            response = json.loads(self._session_sockets[self.session_key].recv(1024).decode())

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

        command = {
            'command': 'LO',
            'user_id': self.user_id,
        }
        response = self.send_command(json.dumps(command))

        if response['Message'] == 'Logged out':
            self.logged_in = False
            self.user_id = None

        return response

    def execute_command(self, command):
        response = self.send_command(json.dumps(command))
        return response
    
    def receive_notification(self):
        while not self.notification_thread_flag.is_set():
            try:
                with self.socket_lock:
                    while True:
                        self._session_sockets[self.session_key].settimeout(0.1)
                        data = json.loads(self._session_sockets[self.session_key].recv(1024).decode())
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
                self._session_sockets[self.session_key].settimeout(None)

    def server_shutdown(self):
        self.notification_thread_flag.set()
        self.notification_thread.join()

        print("\nServer has shutdown. Please exit with CTRL+C")
        command = {}
        command["command"] = "SS_Ack"
        self.send_command(json.dumps(command))

        with self.socket_lock:
            self._session_sockets[self.session_key].close()

        sys.exit(0)

    def signal_handler(self, signal, frame):
        self.notification_thread_flag.set()
        self.notification_thread.join()

        print("\nReceived Ctrl+C. Closing connection...")
        command = {}
        command["command"] = "E"
        self.send_command(json.dumps(command))

        with self.socket_lock:
            self._session_sockets[self.session_key].close()

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
