import cv2 as cv
import numpy as np
import time
import hashlib
import uuid



        ### OBJECT ###
class Object:
    id = -1

    def __init__(self, user, type):
        Object.id += 1

        self.user = user
        self.type = type
        self.id = Object.id

        ### USER ###
class User:
    user_objects = {}
    tok = -1  

    def __init__(self, username, email, fullname, passwd):
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.fullname = fullname
        self.pwd_hash = hashlib.sha256(passwd.encode()).hexdigest()
        self.token = -1
    
        User.user_objects[self.user_id] = self

    def __str__(self):
        return f"User ID: {self.user_id}\nUsername: {self.username}\nEmail: {self.email}\nFull name: {self.fullname}"

    def update(self, username=None, email=None, fullname=None, passwd=None):
        if username:
            self.username = username
        if email:
            self.email = email
        if fullname:
            self.fullname = fullname
        if passwd:
            self.pwd_hash = hashlib.sha256(passwd.encode()).hexdigest()

    def delete(self):
        del User.user_objects[self.user_id]

    def auth(self, plainpass):
        return self.pwd_hash == hashlib.sha256(plainpass.encode()).hexdigest()

    def login(self):
        User.tok = str(uuid.uuid4())  # Generate a unique token
        self.token = User.tok
        return self.token

    def checksession(self, token):
        return token == self.token

    def logout(self):
        self.token = -1

    @classmethod
    def switchuser(cls, user_id):
        if user_id in cls.user_objects:
            return cls.user_objects[user_id]
        else:
            return None

    @classmethod
    def listusers(cls):
        return [(user.user_id, user.username) for user in cls.user_objects.values()]
        

        ### PLAYER OBJECT ###
class Player(Object):

    def __init__(self, user, team, health, repo, map):
        super().__init__(user, "Player")
        self.team = team
        self.health = health
        self.repo = repo
        self.map = map

    def __str__(self):
        repo_str = "\n"
        for i, item in enumerate(self.repo):
            repo_item_str  = "(" + ", ".join((map(str, item))) + ")"
            repo_str = repo_str + repo_item_str
            if(i < len(self.repo) - 1):
                repo_str += "\n"

        output = "Player: \nUser: '" + str(self.user) +  "'\nTeam: '" + self.team + "'\nHealth: " + str(self.health) + "\nRepository: " + repo_str 
        return output

    def updatePositionOfPlayer(self, direction):
        objects_list = self.map.objects_list 
        team_view_object_list = self.map.teams[self.team].objects_list

        if(direction == "W"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (max(0, tpl[0] - 1), tpl[1], tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (max(0, tpl[0] - 1), tpl[1], tpl[2])

        elif(direction == "NW"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (max(0, tpl[0] - 1), min(self.map.height, tpl[1] + 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (max(0, tpl[0] - 1), min(self.map.height, tpl[1] + 1), tpl[2])
        
        elif(direction == "N"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (tpl[0], min(self.map.height, tpl[1] + 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (tpl[0], min(self.map.height, tpl[1] + 1), tpl[2])

        elif(direction == "NE"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (min(self.map.width, tpl[0] + 1), min(self.map.height, tpl[1] + 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (min(self.map.width, tpl[0] + 1), min(self.map.height, tpl[1] + 1), tpl[2])

        elif(direction == "E"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (min(self.map.width, tpl[0] + 1), tpl[1], tpl[2])
            print(self.map.teams[self.team])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (min(self.map.width, tpl[0] + 1), tpl[1], tpl[2])

        elif(direction == "SE"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (min(self.map.width, tpl[0] + 1), max(0, tpl[1] - 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (min(self.map.width, tpl[0] + 1), max(0, tpl[1] - 1), tpl[2])

        elif(direction == "S"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (tpl[0], max(0, tpl[1] - 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (tpl[0], max(0, tpl[1] - 1), tpl[2])

        elif(direction == "SW"):
            for i, tpl in enumerate(objects_list):
                if (tpl[2].id == self.id):
                    objects_list[i] = (max(0, tpl[0] - 1), max(0, tpl[1] - 1), tpl[2])
            for i, tpl in enumerate(team_view_object_list):
                if (tpl[2].id == self.id):
                    team_view_object_list[i] = (max(0, tpl[0] - 1), max(0, tpl[1] - 1), tpl[2])

    def updateBackgroundImage(self):
        for tpl in self.map.objects_list: 
            if (tpl[2].id == self.id):
                x = tpl[0]
                y = tpl[1]
        self.map.teams[self.team].setimage(x, y, 0, self.map.getimage(x,y,0)) 
    
    def move(self, direction):

        self.updatePositionOfPlayer(direction)
        self.updateBackgroundImage()
        # need to query
        self.competition()

        if (self.health <= 0):
            self.map.leave(self.user, self.team)

    def competition(self):   #Will be implemented in next phases.
        return

    def stun(self, stun):
        time.sleep(stun)

    def drop(self, objecttype):

        available_objects = [obj for obj in self.repo if obj[0] == objecttype]
        drop_obj = available_objects[0]
        if(drop_obj):
            for tpl in self.map.objects_list: 
                    if (tpl[2].id == self.id):
                        x = tpl[0]
                        y = tpl[1]
            if (drop_obj[0] == "Health"):
                if max(0, x-5) == x-5:
                    nx = x-5
                    ny = 0
                elif max(0, y-5) == y-5:
                    nx = 0
                    ny = y-5
                elif min(self.map.width, x+5) == x+5:
                    nx = x+5
                    ny = 0
                elif min(self.map.height, y+5) == y+5:
                    nx = 0
                    ny = y+5
                self.map.addHealthObject(nx, ny, drop_obj[1], drop_obj[2])
                self.map.teams[self.team].addHealthObject(nx, ny, drop_obj[1], drop_obj[2])
            if (drop_obj[0] == "Mine"):
                self.map.addMineObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3])
                self.map.teams[self.team].addMineObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3])
            if (drop_obj[0] == "Freezer"):
                self.map.addFreezerObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3])
                self.map.teams[self.team].addFreezerObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3])
        
        self.repo.remove(drop_obj)

        
        ### MINE OBJECT ###
class Mine(Object):
    def __init__(self, p = 5, d = 10, k = 1000):
        super().__init__("Mine", "Mine")
        self.prox = p
        self.dmg = d
        self.itr = k

    def __str__(self):
        output = "Mine: " + "[Proximity: " + str(self.prox) + ", Damage: " + str(self.dmg) + ", Iteration: " + str(self.itr) + "]"
        return output

    def run(self, map):
        time.sleep(1)
        for tpl in map.objects_list:
            if (tpl[2].id == self.id):
                x = tpl[0]
                y = tpl[1]
        exploded = False
        for i in range(self.itr):
            for obj in map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    obj[2].health -= self.dmg
                    exploded = True
            if(exploded):
                break
        map.removeObject(self.id)
            

        ### FREEZER OBJECT ###
class Freezer(Object):
    def __init__(self, p = 5, d = 10, k = 1000):
        super().__init__("Freezer", "Freezer")
        self.prox = p
        self.stun = d
        self.itr = k

    def __str__(self):
        output = "Freezer: " + "[Proximity: " + str(self.prox) + ", Damage: " + str(self.stun) + ", Iteration: " + str(self.itr) + "]"
        return output
    
    def run(self, map):
        time.sleep(0.1)
        for tpl in map.objects_list: 
             if (tpl[2].id == self.id):
                x = tpl[0]
                y = tpl[1]
        stunned = False
        for i in range(self.itr):
            for obj in map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    stunned = True
                    obj[2].stun(self.stun)
            if(stunned):
                break
        map.removeObject(self.id)

        
        ### HEALTH OBJECT ###
class Health(Object):
    def __init__(self, m = 30, inf = True):
        super().__init__("Freezer", "Health")
        self.health = m
        self.cap = inf

    def __str__(self):
        output = "Health: " + "[Health Capacity: " + str(self.health) + ", Infinite: " + str(self.cap) + "]"
        return output
    
    def run(self, map):
        for tpl in map.objects_list: 
            if (tpl[2].id == self.id):
                x = tpl[0]
                y = tpl[1]
        cond = True
        while(cond):
            for obj in map.query(x, y, 3): 
                if(obj[2].type == "Player"):
                    obj[2].health += self.health
                    if(self.cap == False):
                        cond = False
        map.removeObject(self.id)


        ### MAP ###
    
class Map:
    id = -1

    def __init__(self, name, size, config):
        Map.id += 1
        self.map_id = Map.id
        self.name = name
        self.width, self.height = size
        self.bg_img = np.zeros((self.height,self.width,3), np.uint8)
        self.objects_list = []
        self.teams = {}
        self.player_vision = 5
        self.player_health = 100
        self.player_repo = []
        self.config = config
        self.parse_config(config)
        self.initializeObjects()

    def __str__(self):
        teams_str = "\n".join(self.teams) 
        
        objects_str = ""
        for i, item in enumerate(self.objects_list):
            objects_item_str = "(" + ", ".join((map(str, item))) + ")"
            objects_str += objects_item_str
            if(i < len(self.objects_list) - 1):
                objects_str += "\n"

        repo_str = ""
        for i, item in enumerate(self.player_repo):
            repo_item_str  = "(" + ", ".join((map(str, item))) + ")"
            repo_str = repo_str + repo_item_str
            if(i < len(self.player_repo) - 1):
                repo_str += "\n"
        
        output = "MAP\nid: " + str(self.map_id) + "\nName: " + self.name + "\nSize: (W: " + str(self.width) + ", H: " + str(self.height) + ")\nTeams On The Map:\n" + teams_str + "\nObjects In The Map:\n" + objects_str + "\nPlayer Vision: " + str(self.player_vision) + "\nPlayer Health: " + str(self.player_health) + "\nPlayer Repository:\n" + repo_str 
        return output
    
    def initializeObjects(self):
        for obj in self.objects_list:
            if(obj[2].__class__.__name__ != 'Player'):
                obj[2].run(self)

    def parse_config(self, config):
        if config:
            if ('image' in config):
                bg_img = cv.imread(config['image'])
                if(bg_img is not None and bg_img.shape[0] == self.height and bg_img.shape[1] == self.width):
                    self.bg_img = bg_img
            if ('playervision' in config):
                self.player_vision = config['playervision']
            if ('playerh' in config):
                self.player_health = config['playerh']
            if ('playerrepo' in config):
                self.player_repo = config['playerrepo']
            if ('objects' in config):
                self.objects_list = config['objects']
            
    def addObject(self, type, x, y):
        if (type == "Health"):
            healthObject = Health()
            self.objects_list.append((x,y,healthObject))
            healthObject.run(self)
        if (type == "Mine"):
            mineObject = Mine()
            self.objects_list.append((x,y,mineObject))
            mineObject.run(self)
        if (type == "Freezer"):
            freezerObject = Freezer()
            self.objects_list.append((x,y,freezerObject))
            freezerObject.run(self)

    def addHealthObject(self, x, y, health_val, inf):
        healthObject = Health(health_val, inf)
        self.objects_list.append((x, y, healthObject))
        healthObject.run(self)
    
    def addMineObject(self, x, y, p, d, k):
        mineObject = Mine(p, d, k)
        self.objects_list.append((x, y, mineObject))
        mineObject.run(self)

    def addFreezerObject(self, x, y, p, s, k):
        freezerObject =  Freezer(p, s, k)
        self.objects_list.append((x, y, freezerObject))
        freezerObject.run(self)

    def addPlayerObject(self, x, y, p):
        self.objects_list.append((x, y, p))
    
    def removeObject(self, id):
        self.objects_list = [obj for obj in self.objects_list if obj[2].id != id]

    def listObjects(self):
        return iter([(obj[2].id, obj[2].user, obj[2].type, obj[0], obj[1]) for obj in self.objects_list])
    
    def getimage(self, x, y, r):
        r = self.player_vision if r == 0 else r
        
        if (self.bg_img is None):
            return None

        return self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)]
    
    def setimage(self, x, y, r, image):
        r = self.player_vision if r == 0 else r

        if (self.bg_img is None or image is None):
            return
        self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)] = image
    
    def query(self, x, y, r):
        if(r == 0):
           r = self.player_vision

        new_objects_list = [obj for obj in self.objects_list if (max(0, x-r) <= obj[0] <= min(x+r,self.width) and (max(0,y-r) <= obj[1] <= min(self.height,y+r)))]
        return new_objects_list
    
    def join(self, player, team):
        
        for object in self.objects_list:
            if(object[2].__class__.__name__ == 'Player' and object[2].user == player):
                return None

        if (team not in self.teams):  
            team_map = Map(f'{self.name} (Team View {team})', (self.width, self.height), self.config)
            
            team_map.bg_img = np.zeros((self.height,self.width,3), np.uint8)  #Initialize the map as blank image
            team_map.setimage(0, 0, 0, self.getimage(0,0,0))

            self.teams[team] = team_map

        p = Player(player, team, self.player_health, self.player_repo[:], self)
        self.objects_list.append((0, 0, p))
        self.teammap(team).addPlayerObject(0, 0, p) #Add player to team_map as well.
        return p

    def leave(self, player, team):
        for object in self.objects_list:
            if(object[2].__class__.__name__ == 'Player' and object[2].user == player and object[2].team == team):
                self.removeObject(object[2].id)
        return
    
    def teammap(self, team):
        return self.teams.get(team)
    