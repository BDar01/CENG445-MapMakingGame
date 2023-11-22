import cv2 as cv
import numpy as np
import time

       ### OBJECT ###
class Object:
    id = -1

    def __init__(self, name, type):
        Object.id += 1

        self.name = name
        self.type = type
        self.id = Object.id
        

        ###  PLAYER OBJECT ###

class Player(Object):

    def __init__(self, user, team, health, repo, map):
        super().__init__(user, "Player")
        self.username = user
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

        output = "Player: \nUsername: '" + self.username +  "'\nTeam: '" + self.team + "'\nHealth: " + str(self.health) + "\nRepository: " + repo_str 
        return output

    def updatePositionOfPlayer(self, direction):
        objects_list = self.map.objects_list # need global map
        object_list_length = len(objects_list)

        if(direction == "W"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] - 1, tpl[1], tpl[2])

        elif(direction == "NW"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] - 1, tpl[1] + 1, tpl[2])
        
        elif(direction == "N"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0], tpl[1] + 1, tpl[2])

        elif(direction == "NE"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1] + 1, tpl[2])

        elif(direction == "E"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1], tpl[2])

        elif(direction == "SE"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1] - 1, tpl[2])

        elif(direction == "S"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0], tpl[1] - 1, tpl[2])

        elif(direction == "SW"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] - 1, tpl[1] - 1, tpl[2])

    def updateBackgroundImage(self):
        for tpl in self.map.objects_list: # need global map
            if tpl[2].id == self.id:
                x = tpl[0]
                y = tpl[1]
        self.map.setimage(x, y, 0, self.map.getimage(x,y,0)) # need global map
    
    def move(self, direction):

        self.updatePositionOfPlayer(direction)
        self.updateBackgroundImage(direction)
        # need to query
        self.competition()

        if (self.health <= 0):
            self.map.leave(self.username, self.team)

    def competition(self):   #Will be implemented in next phases.
        return

    def stun(self, stun):
        time.sleep(stun)

    def drop(self, objecttype):

        available_objects = [obj for obj in self.repo if obj[0] == objecttype]
        drop_obj = available_objects[0]
        if(drop_obj):
            for tpl in self.map.objects_list: 
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            if (drop_obj[0] == "Health"):
                self.map.addHealthObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3])
            if (drop_obj[0] == "Mine"):
                self.map.addMineObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3], drop_obj[4])
            if (drop_obj[0] == "Freezer"):
                self.map.addFreezerObject(x, y, drop_obj[1], drop_obj[2], drop_obj[3], drop_obj[4])
        
        self.repo.remove(drop_obj)

        ### MINE OBJECT ###

class Mine(Object):
    def __init__(self, name, p = 5, d = 10, k = 1000):
        super().__init__(name, "Mine")
        self.prox = p
        self.dmg = d
        self.itr = k

    def __str__(self):
        output = "Mine: " + "[Name: '" + self.name + "', Proximity: " + str(self.prox) + ", Damage: " + str(self.dmg) + ", Iteration: " + str(self.itr) + "]"
        return output

    def run(self, map):
        time.sleep(1)
        for tpl in map.objects_list:
            if tpl[2].id == self.id:
                x = tpl[0]
                y = tpl[1]
        for i in range(self.itr):
            for obj in map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    obj[2].health -= self.dmg
                    break
            break

        ### FREEZER OBJECT ###

class Freezer(Object):
    def __init__(self, name, p = 5, d = 10, k = 1000):
        super().__init__(name, "Freezer")
        self.prox = p
        self.stun = d
        self.itr = k

    def __str__(self):
        output = "Freezer: " + "[Name: '" + self.name + "', Proximity: " + str(self.prox) + ", Damage: " + str(self.stun) + ", Iteration: " + str(self.itr) + "]"
        return output
    
    def run(self, map):
        time.sleep(0.1)
        for tpl in map.objects_list: 
             if tpl[2].id == self.id:
                x = tpl[0]
                y = tpl[1]
        for i in range(self.itr):
            for obj in map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    obj[2].stun(self.stun)

        ### HEALTH OBJECT ###

class Health(Object):
    def __init__(self, name, m = 30, inf = True):
        super().__init__(name, "Health")
        self.health = m
        self.cap = inf

    def __str__(self):
        output = "Health: " + "[Name: '" + self.name + "', Health Capacity: " + str(self.health) + ", Infinite: " + str(self.cap) + "]"
        return output
    
    def run(self, map):
            for tpl in map.objects_list: # need global map
                if tpl[2].id == self.id:
                    x = tpl[0]
                    y = tpl[1]
            cond = True
            while(cond):
                for obj in map.query(x, y, 3): # need global map
                    if(obj[2].type == "Player"):
                        obj[2].health += self.health
                        if(self.cap == False):
                            cond = False








class Map:
    def __init__(self, name, size, config):
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
        
        output = "MAP\nName: " + self.name + "\nSize: (W: " + str(self.width) + ", H: " + str(self.height) + ")\nTeams On The Map:\n" + teams_str + "\nObjects In The Map:\n" + objects_str + "\nPlayer Vision: " + str(self.player_vision) + "\nPlayer Health: " + str(self.player_health) + "\nPlayer Repository:\n" + repo_str 
        return output
    
    def initializeObjects(self):
        for obj in self.objects_list:
            if(obj[2].__class__.__name__ != 'Player'):
                obj[2].run()

    def parse_config(self, config):
        if config:
            if 'image' in config:
                bg_img = cv.imread(config['image'])
                if(len(bg_img) > 0 and bg_img.shape[0] == self.height and bg_img.shape[1] == self.width):
                    self.bg_img = bg_img
            if 'playervision' in config:
                self.player_vision = config['playervision']
            if 'playerh' in config:
                self.player_health = config['playerh']
            if 'playerrepo' in config:
                self.player_repo = config['playerrepo']
            if 'objects' in config:
                self.objects_list = config['objects']
            
    def addObject(self, name, type, x, y):
        if (type == "Health"):
            healthObject = Health(name)
            self.objects_list.append((x,y,healthObject))
            healthObject.run()
        if (type == "Mine"):
            mineObject = Mine(name)
            self.objects_list.append((x,y,Mine(name)))
            mineObject.run()
        if (type == "Freezer"):
            freezerObject = Freezer(name)
            self.objects_list.append((x,y,freezerObject))
            freezerObject.run()

    def addHealthObject(self, x, y, name, health_val, inf):
        healthObject = Health(name, health_val, inf)
        self.objects_list.append((x, y, healthObject))
        healthObject.run(self)
    
    def addMineObject(self, x, y, name, p, d, k):
        mineObject = Mine(name, p, d, k)
        self.objects_list.append((x, y, mineObject))
        mineObject.run(self)

    def addFreezerObject(self, x, y, name, p, s, k):
        freezerObject =  Freezer(name, p, s, k)
        self.objects_list.append((x, y, freezerObject))
        freezerObject.run(self)
    
    def removeObject(self, id):
        self.objects_list = [obj for obj in self.objects_list if obj[2].id != id]

    def listObjects(self):
        return iter([(obj[2].id, obj[2].name, obj[2].type, obj[0], obj[1]) for obj in self.objects_list])
    
    def getimage(self, x, y, r):
        r = self.player_vision if r == 0 else r
        
        if len(self.bg_img) == 0:
            return None

        return self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)]
    
    def setimage(self, x, y, r, image):
        r = self.player_vision if r == 0 else r

        if len(self.bg_img) == 0 or image is None:
            return
        self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)] = image
    
    def query(self, x, y, r):
        if(r == 0):
           r = self.player_vision

        new_objects_list = [obj for obj in self.objects_list if (max(0, x-r) <= obj[0] <= min(x+r,self.width) and (max(0,y-r) <= obj[1] <= min(self.height,y+r)))]
        return iter(new_objects_list)
    
    def join(self, player, team):
        
        for object in self.objects_list:
            if(object[2].__class__.__name__ == 'Player' and object[2].username == player):
                return None


        if team not in self.teams:  
            team_map = Map(f'{self.name} (Team View {team})', (self.width, self.height), self.config)
            
            team_map.bg_img = np.zeros((self.height,self.width,3), np.uint8)  #Initialize the map as blank image
            team_map.setimage(0, 0, 0, self.getimage(0,0,0))

            self.teams[team] = team_map

        p = Player(player, team, self.player_health, self.player_repo, self.teams[team])
        self.objects_list.append((0, 0, p))
        
        return p

    def leave(self, player, team):
        for object in self.objects_list:
            if(object[2].__class__.__name__ == 'Player' and object[2].username == player and object[2].team == team):
                self.removeObject(object[2].id)
        return
    
    def teammap(self, team):
        return self.teams.get(team)
    


