from object import *
import cv2 as cv
import numpy as np

class Map:
    def __init__(self, name, size, config):
        self.name = name
        self.width, self.height = size
        self.bg_img = np.zeros((self.height,self.width,3), np.uint8)
        self.objects_list = []
        self.teams = {}
        self.player_vision = 5
        self.default_player_health = 100
        self.default_player_repo = []
        self.parse_config(config)

    def parse_config(self, config):
        if config:
            if 'image' in config:
                bg_img = cv.imread(config.image)
                if(bg_img and bg_img.shape[0] == self.height and bg_img.shape[1] == self.width):
                    self.bg_img = bg_img
                    
            if 'playervision' in config:
                self.player_vision = config['playervision']
            if 'playerh' in config:
                self.default_player_health = config['playerh']
            if 'playerrepo' in config:
                self.default_player_repo = config['playerrepo']
            if 'objects' in config:
                self.objects_list = [Object(*obj) for obj in config['objects']]

    def addObject(self, name, type, x, y):
        if (type == "Health"):
            self.objects_list.append((x,y,Health(name)))
        if (type == "Mine"):
            self.objects_list.append((x,y,Mine(name)))
        if (type == "Freezer"):
            self.objects_list.append((x,y,Freezer(name)))
    
    def removeObject(self, id):
        self.objects_list = [obj for obj in self.objects_list if obj[2].id != id]

    def listObjects(self):
        return iter([(obj[2].id, obj[2].name, obj[2].type, obj[0], obj[1]) for obj in self.objects_list])
    
    def getimage(self, x, y, r):
        r = self.player_vision if r is None else r

        if self.bg_img is None:
            return None

        return self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)]
    
    def setimage(self, x, y, r, image):
        r = self.player_vision if r == 0 else r

        if self.bg_img or image is None:
            return

        self.bg_img[max(0, y - r):min(self.height, y + r), max(0, x - r):min(self.width, x + r)] = image
    
    def query(self, x, y, r):
        if(r == 0):
           r = self.config.playervision

        new_objects_list = [obj for obj in self.objects_list if (max(0, x-r) <= obj[0] <= min(x+r,self.width) and (max(0,y-r) <= obj[1] <= min(self.height,y+r)))]
        return iter(new_objects_list)
    
    def join(self, player, team):
        if player in [p[2].user for p in self.objects_list]:
            return None

        if team not in self.teams:
            team_map = Map(f'Team {team} Map', (self.width, self.height))
            
            team_map.bg_img = np.zeros((self.height,self.width,3), np.uint8)
            team_map.bg_img.setimage(0, 0, 0, self.getimage(0,0,0))

            self.teams[team] = team_map

        p = Player(player, team, self.default_player_health, self.default_player_repo, self.teams[team])
        self.objects_list.append((0,0,p))

        return p

    def leave(self, player, team):
        id = [obj[2].id for obj in self.objects_list if obj[2].name == player and obj[2].team == team]

        if(id): 
            id = id[0]
            self.removeObject(id)
        else:
            id = None

        return
    
    def teammap(self, team):
        return self.teams.get(team)
