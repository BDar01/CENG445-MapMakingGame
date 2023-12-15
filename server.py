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
import config
from singleton import UserFactory
from singleton import MapFactory

thread_local = threading.local()

def get_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value.username == target_value:
            return key, value
            
class GameServer:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(5)
        self.server.settimeout(1.0)
        self.games = {}  # Store game instances
        self.user_sockets = {}  # Store user sockets for notifications
        self.notification_queues = {}  # Store notification queues for each user
        self.port = port
        self.shutdown_flag = threading.Event()
        # Register the signal handler for CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)
        #self.config_templates = self.load_config_templates() # Load configuration templates from a file (config.json) - NOT IMPLEMENTED YET
        self.load_state()
    '''def load_config_templates(self):
        # Load configuration templates from a file (config.json)
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        return config_data
    '''

    
    def signal_handler(self, signal, frame):
        print("Received Ctrl+C. Closing connection...")
        self.save_state()
        self.shutdown_flag.set()
        self.server.close()
        sys.exit(0)
    
    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db_exists = os.path.isfile('server.sql3')

        with sqlite3.connect('server.sql3') as db: 
            c = db.cursor()

            if not db_exists:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        fullname TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                ''')
                db.commit()

            try:
                c.execute('SELECT * FROM users WHERE username=?', (username,))
                row = c.fetchone()
            except sqlite3.Error as e:
                print(f"Error executing SQL query: {e}")
                row = None

        if row and hashed_password == row[2]:
            return True
        return False


    def register_user(self, username, email, fullname, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with sqlite3.connect('server.sql3') as db:
            c = db.cursor()

            try:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        fullname TEXT NOT NULL,
                        email TEXT NOT NULL
                    )
                ''')

                c.execute("INSERT INTO users (username, password, fullname, email) VALUES (?, ?, ?, ?)", (username, hashed_password, fullname, email))
                db.commit()

            except sqlite3.Error as e:
                print(f"Error executing SQL query: {e}")

       
    def serialize_user(self, user):
        return {"user_id":  user.user_id, "username": user.username, "email": user.email, "fullname": user.fullname, "pwd_hash": user.pwd_hash, "token": user.token}

    def serialize_mine(self, object):
        return {"Proximity": object.prox, "Damage": object.dmg, "Lifetime": object.itr}
    
    def serialize_freezer(self, object):
        return {"Proximity": object.prox, "Stun": object.stun, "Lifetime": object.itr}

    def serialize_health(self, object):
        return {"Health": object.health, "Lifetime": object.cap}

        
    def serialize_config(self, config):
        serialized_config = {}
        for key, value in config.items():
            if key == "objects":
                objects = value
                serialized_objects = []
                for object in objects:
                    if isinstance(object[2], Mine):
                        serialized_objects.append([object[0], object[1], self.serialize_mine(object[2])])
                    elif isinstance(object[2], Freezer):
                        serialized_objects.append([object[0], object[1],self.serialize_freezer(object[2])])
                    elif isinstance(object[2], Health):
                        serialized_objects.append([object[0], object[1],self.serialize_health(object[2])])

                serialized_config[key] = serialized_objects

            else:
                serialized_config[key] = value


        return serialized_config
            
    
    def handle_game_command(self, user, data):
        try:
            if data['command'] == "listusers":
                return json.dumps({"Message":[({"user_id": user_id, "username": user.username, "email": user.email, "fullname": user.fullname}) for user_id, user in UserFactory().user_list.items()]})

            elif data['command'] == "move":
                if len(data.items()) != 3:
                    raise ValueError("Invalid number of parameters for move command")
                user_id, direction = data['user_id'], data['direction']
                user = UserFactory().user_list[user_id]
                player = user.player
                player.move(direction)
                return json.dumps({"Message": f"Player {user.username} moved {direction}"})

            elif data['command'] == "drop":
                if len(data.items()) != 3:
                    raise ValueError("Invalid number of parameters for drop command")
                user_id, object_type = data['user_id'], data['object_type']
                user = UserFactory().user_list[user_id]
                player = user.player
                player.drop(object_type)
                return json.dumps({"Message": f"Player {user.username} dropped {object_type}"})

            elif data['command'] == "querymap":
                if len(data.items()) != 5:
                    raise ValueError("Invalid number of parameters for querymap command")
                user_id, x, y, radius = data['user_id'], data['x'], data['y'], data['radius']
                user = UserFactory().user_list[user_id]
                player = user.player
                objects_in_radius = player.map.query(int(x), int(y), int(radius))
                return json.dumps({"Message":[(obj[2].id, obj[2].type, obj[0], obj[1]) for obj in objects_in_radius]})

            elif data['command'] == "newmap":
                if len(data.items()) != 4:
                    raise ValueError("Invalid number of parameters for newmap command")
                map_name, map_size, config_template = data['map_name'], data['map_size'], data['config_template']
                map_size = tuple(map(int, map_size.split('x')))
                new_map = MapFactory().new(map_name, map_size, config.MAPS[config_template])
                return json.dumps({"Message": f"Map {new_map.name} created with ID: {new_map.map_id}"})

            elif data['command'] == "listmaps":
                if len(MapFactory().map_list.items()) == 0:
                    return json.dumps({"Message": "No map found."})
                return json.dumps({"Message": [({"map_id": map_id, "map_name": game_map.name, "map_size": (game_map.width, game_map.height),"map_teams": list(game_map.teams.keys()), "map_config": self.serialize_config(game_map.config)}) for map_id, game_map in MapFactory().map_list.items()]})

            elif data['command'] == "joinmap":
                if len(data.items()) != 4:
                    raise ValueError("Invalid number of parameters for joinmap command")
                user_id, map_id, teamname = data['user_id'], int(data['map_id']), data['teamname']

                user = UserFactory().user_list[user_id]
                if map_id in list(MapFactory().map_list.keys()):
                    my_map = MapFactory().map_list[map_id]
                    p = my_map.join(user.username, teamname)
                    if(p == None):
                        return json.dumps({"Message":"User already exists in the map."})
                    else:
                        user.player = p
                        return json.dumps({"Message": f"User '{user.username}' (Team member of {teamname}) joined to '{my_map.name}'."})

                else:
                    return json.dumps({"Message": f"Map {map_id} not found"})

            #elif data['command'] == "notify":
            #    message = " ".join(params)
            #    self.send_notification(user, message)


            elif data['command'] == "LO":
                user_id = data["user_id"]
                UserFactory().user_list[user_id].logout()
                thread_local.authenticated_user = None
                response = json.dumps({"Message": "Logged out"})
                return response

            elif data['command'] == "E":
                thread_local.is_connected = False
                response = json.dumps({"Message": "Exit"})
                return response

            else:
                return json.dumps({"Message": "Invalid command. Try again."})

        except Exception as e:
            return json.dumps({"Message": f"Error: {str(e)}"})

    def send_notification(self, user, message):
        if user in self.user_sockets:
            notification_queue = self.notification_queues[user]
            notification_queue.append(message)
            user_socket = self.user_sockets[user]
            user_socket.send(f"NOTIFY {message}".encode())

    def handle_client(self, client_socket):
        notification_queue = []

        thread_local.is_connected = True
        thread_local.authenticated_user = None

        try:
            while thread_local.is_connected:
                if not thread_local.authenticated_user and not self.shutdown_flag.is_set():
                    try:
                        client_socket.settimeout(1.0)
                        data = json.loads(client_socket.recv(1024).decode())
                        if data:
                            command = data["command"]
                            if command == "L":
                                username = data["username"]
                                password = data["password"]

                                if self.authenticate_user(username, password):
                                    thread_local.authenticated_user = username
                                    self.user_sockets[thread_local.authenticated_user] = client_socket
                                    self.notification_queues[thread_local.authenticated_user] = notification_queue
                                    user_id, user = get_key_by_value(UserFactory().user_list, username)
                                    token = user.login()
                                    response = json.dumps({'Message' : "Logged in", 'user_id': user_id, 'token': token})
                                    client_socket.send(response.encode())
                                else:
                                    client_socket.send("Authentication failed".encode())

                            elif command == "R":
                                username = data["username"]
                                password = data["password"]
                                email = data["email"]
                                fullname = data["fullname"] 

                                if(get_key_by_value(UserFactory().user_list, username)):
                                    response = json.dumps({'Message': "Username exists. Please try for another username."})
                                    client_socket.send(response.encode())                                    
                                else:
                                    self.register_user(username, email, fullname, password)
                                    user = UserFactory().new(username, email, fullname, password)
                                    response = json.dumps({'Message' : "User added successfully. Please login."})
                                    client_socket.send(response.encode())

                            elif command == "C":
                                user_id = data["user_id"]
                                token = data["token"]

                                if (UserFactory().user_list[user_id].checksession(token)):

                                    response = json.dumps({'Message' : "Logged in", 'user_id': user_id, 'token': token})

                                    thread_local.authenticated_user = UserFactory().user_list[user_id].username

                                    self.user_sockets[thread_local.authenticated_user] = client_socket

                                    client_socket.send(response.encode())  

                                
                                else:
                                    response = json.dumps({'Message': "Authentication Failed."})
                                    client_socket.send(response.encode())  

                            elif command == "E":
                                thread_local.is_connected = False
                                response = json.dumps({'Message' : "Exit"})
                                client_socket.send(response.encode())

                            else:
                                response = json.dumps({'Message' : "Invalid command. Try again."})
                                client_socket.send(response.encode())

                    except socket.timeout:
                        if self.shutdown_flag.is_set():
                            break

                    except Exception as e:
                        print(f"Error: {e}")

                if thread_local.authenticated_user and not self.shutdown_flag.is_set():
                    try:
                        client_socket.settimeout(1.0)
                        response = client_socket.recv(1024).decode()
                        data = json.loads(response)
            
                        if data:

                            response = self.handle_game_command(thread_local.authenticated_user, data)

                            client_socket.send(response.encode())

                    except socket.timeout:
                        if self.shutdown_flag.is_set():
                            break

        except ConnectionResetError:
            print("Client disconnected unexpectedly.")
        finally:
            client_socket.close()

    def start_server(self):
        print(f"Server listening on port {self.port}...")
        while not self.shutdown_flag.is_set():
            try:
                client_socket, addr = self.server.accept()
                print(f"Accepted host: {client_socket.getpeername()}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=False)
                client_handler.start()
            except socket.timeout:
                 if self.shutdown_flag.is_set():
                    break

    def save_state(self):
        #Save the user_list
        state_data = {
            'users': json.dumps([self.serialize_user(user) for _, user in UserFactory().user_list.items()]),
            'maps':  json.dumps([(map_id, game_map.name, (game_map.width, game_map.height), {"teams": list(game_map.teams.keys())}, self.serialize_config(game_map.config)) for map_id, game_map in MapFactory().map_list.items()]),
            'games': json.dumps([(map_id, map.name, (map.width, map.height), self.serialize_config(map.config)) for map_id, map in self.games.items()])
        }

        with open("server_state.json", 'w') as file:
            json.dump(state_data, file)

    def load_state(self):
        ##Loads the user_list
        try:
            with open("server_state.json", 'r') as file:
                state_data = json.load(file)

                # Restore user list
                user_list = json.loads(state_data['users'])
                for user in user_list:
                    user_id, username, email, fullname, pwd_hash, token = user['user_id'], user['username'], user['email'], user['fullname'], user['pwd_hash'], user['token']
                    UserFactory().new_from_load(user_id, username, email, fullname, pwd_hash, token)
                    
                map_list = json.loads(state_data['maps'])
                # Restore map list
                for map in map_list:
                    map_id = map[0]
                    map_name = map[1]
                    [map_width, map_height] = map[2]
                    map_teams = map[3]
                    map_config = map[4]
                    objects = map_config['objects']
                    for i in objects:
                        object_dict = i[2]
                        keys = list(object_dict.keys())
                        if("Damage" in keys):
                            mine = Mine(object_dict['Proximity'], object_dict['Damage'], object_dict['Lifetime'])
                            i[2] = mine
                        elif("Stun" in keys):
                            freezer = Freezer(object_dict['Proximity'], object_dict['Stun'], object_dict['Lifetime'])
                            i[2] = freezer
                        elif("Health" in keys):
                            health = Health(object_dict['Health'], object_dict['Lifetime'])
                            i[2] = health
                    
                    MapFactory().new_from_load(map_name, (map_width, map_height), map_config, map_id)
                    

        except FileNotFoundError:
            pass
        except Exception as e:
            pass
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Game Server')
    parser.add_argument('--port', type=int, default=1423, help='Port number to listen on')
    args = parser.parse_args()

    server = GameServer(args.port)
    server.start_server()