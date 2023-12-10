import socket
import threading
import json
import struct
import hashlib
import sqlite3
import argparse
import signal
import sys
import os
from game import *

class GameServer:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(5)
        self.games = {}  # Store game instances
        self.user_sockets = {}  # Store user sockets for notifications
        self.notification_queues = {}  # Store notification queues for each user
        self.port = port
        # Register the signal handler for CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)
        #self.config_templates = self.load_config_templates() # Load configuration templates from a file (config.json) - NOT IMPLEMENTED YET
    
    '''def load_config_templates(self):
        # Load configuration templates from a file (config.json)
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        return config_data
    '''

    def signal_handler(self, signal, frame):
        print("Received Ctrl+C. Closing connection...")
        self.close()
        sys.exit(0)
    
    def authenticate_user(self, username, password):
        db_exists = os.path.isfile('project.sql3')

        with sqlite3.connect('project.sql3') as db: 
            c = db.cursor()

            if not db_exists:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )
                ''')
                db.commit()

            try:
                c.execute('SELECT * FROM users WHERE username=?', (username,))
                row = c.fetchone()
            except sqlite3.Error as e:
                print(f"Error executing SQL query: {e}")
                row = None

        if row and hashlib.sha256(password.encode()).hexdigest() == row[2]:
            return True
        return False


    def add_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        with sqlite3.connect('project.sql3') as db:
            c = db.cursor()

            try:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )
                ''')

                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                db.commit()

            except sqlite3.Error as e:
                print(f"Error executing SQL query: {e}")


    def handle_game_command(self, user, command, params):
        try:
            if command == "listusers":
                return json.dumps([(user_id, user.username, user.email, user.fullname) for user_id, user in UserFactory().user_list.items()])

            elif command == "newplayer":
                if len(params) != 4:
                    raise ValueError("Invalid number of parameters for newplayer command")
                username, email, fullname, passwd = params
                hashed_password = hashlib.sha256(passwd.encode()).hexdigest()
                user = UserFactory().new(username, email, fullname, hashed_password)
                return f"Player {username} created with ID: {user.user_id}"

            elif command == "move":
                if len(params) != 2:
                    raise ValueError("Invalid number of parameters for move command")
                user_id, direction = params
                user = UserFactory().get(user_id)
                player = user.get_player()
                player.move(direction)
                return f"Player {user.username} moved {direction}"

            elif command == "drop":
                if len(params) != 2:
                    raise ValueError("Invalid number of parameters for drop command")
                user_id, object_type = params
                user = UserFactory().get(user_id)
                player = user.get_player()
                player.drop(object_type)
                return f"Player {user.username} dropped {object_type}"

            elif command == "querymap":
                if len(params) != 4:
                    raise ValueError("Invalid number of parameters for querymap command")
                user_id, x, y, radius = params
                user = UserFactory().get(user_id)
                player = user.get_player()
                objects_in_radius = player.map.query(int(x), int(y), int(radius))
                return json.dumps([(obj[2].id, obj[2].type, obj[0], obj[1]) for obj in objects_in_radius])

            elif command == "newmap":
                if len(params) != 3:
                    raise ValueError("Invalid number of parameters for newmap command")
                map_name, map_size, config_template = params
                map_size = tuple(map(int, map_size.split('x')))
                new_map = MapFactory().new(map_name, map_size, config_template)
                self.games[new_map.map_id] = new_map
                return f"Map {new_map.name} created with ID: {new_map.map_id}"

            elif command == "listmaps":
                return json.dumps([(map_id, game_map.name, game_map.size, game_map.config) for map_id, game_map in MapFactory.map_list.items()])

            elif command == "joinmap":
                if len(params) != 2:
                    raise ValueError("Invalid number of parameters for joinmap command")
                user_id, map_id = params
                user = UserFactory().get(user_id)
                player = user.get_player()
                game_map = self.games.get(int(map_id))
                if game_map:
                    game_map.join(player, player.team)
                    return f"Player {user.username} joined map {game_map.name}"
                else:
                    return f"Map {map_id} not found"

            elif command == "notify":
                message = " ".join(params)
                self.send_notification(user, message)

            elif command == "save_state":
                self.save_state(user)

            elif command == "load_state":
                self.load_state(user)

            else:
                return "Invalid command"

        except Exception as e:
            return f"Error: {str(e)}"

    def send_notification(self, user, message):
        if user in self.user_sockets:
            notification_queue = self.notification_queues[user]
            notification_queue.append(message)
            user_socket = self.user_sockets[user]
            user_socket.send(f"NOTIFY {message}".encode())

    def handle_client(self, client_socket):
        authenticated_user = None
        notification_queue = []

        try:
            while not authenticated_user:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                command, *params = data.split()
                if command == "login":
                    username, password = params
                    if self.authenticate_user(username, password):
                        authenticated_user = username
                        self.user_sockets[authenticated_user] = client_socket
                        self.notification_queues[authenticated_user] = notification_queue
                        client_socket.send("OK".encode())
                    else:
                        client_socket.send("Authentication failed".encode())
                elif command == "adduser":
                    username, password = params
                    self.add_user(username, password)
                    client_socket.send("User added successfully. Please login.".encode())
                else:
                    client_socket.send("Authentication required".encode())

            # Main command loop
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                command, *params = data.split()

                response = self.handle_game_command(authenticated_user, command, params)

                client_socket.send(response.encode())

        except ConnectionResetError:
            print("Client disconnected unexpectedly.")
        finally:
            client_socket.close()

    def start_server(self):
        print(f"Server listening on port {self.port}...")
        while True:
            client_socket, addr = self.server.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
            client_handler.start()

    def save_state(self, user):
        state_data = {
            'users': UserFactory().user_list,
            'maps': MapFactory.map_list,
            'games': self.games
        }

        with open(f"{user.username}_state.json", 'w') as file:
            json.dump(state_data, file)

    def load_state(self, user):
        try:
            with open(f"{user.username}_state.json", 'r') as file:
                state_data = json.load(file)

                # Restore user list
                for user_id, user_data in state_data.get('users', {}).items():
                    UserFactory().load(int(user_id), user_data['username'], user_data['email'], user_data['fullname'])

                # Restore map list
                for map_id, map_data in state_data.get('maps', {}).items():
                    MapFactory().load(int(map_id), map_data['name'], map_data['size'], map_data['config'])

                # Restore game instances
                self.games = state_data.get('games', {})

            self.send_notification(user.user_id, "State loaded successfully")

        except FileNotFoundError:
            self.send_notification(user.user_id, "No saved state found for the user")

        except Exception as e:
            self.send_notification(user.user_id, f"Error loading state: {str(e)}")        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Game Server')
    parser.add_argument('--port', type=int, default=1423, help='Port number to listen on')
    args = parser.parse_args()

    server = GameServer(args.port)
    server.start_server()