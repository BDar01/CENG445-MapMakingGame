from map import Map
import time

class Object:
    id = -1

    def __init__(self, name, type):
        Object.id += 1

        self.name = name
        self.type = type
        self.id = Object.id
        
class Player(Object):

    def __init__(self, user, team, health, repo, map):
        self.name = user
        self.type = "Player"
        self.team = team
        self.health = health
        self.repo = repo
        self.map = map

    def updatePositionOfPlayer(self, direction):
        objects_list = self.map.objects_list
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

    def updateBackgroundImage(self, direction):
        return
    
    def move(self, direction):

        self.updatePositionOfPlayer(direction)
        self.updateBackgroundImage(direction)
        self.competition()

        if (self.health <= 0):
            self.map.leave(self.user.team)

    def competition(self):
        return

    def stun(self, stun):
        time.sleep(stun)

    def drop(self, objecttype):

        available_objects = [obj for obj in self.repo if obj[0] == objecttype]

        if(len(available_objects) > 0):
            return
        
        drop_obj = available_objects[0]
        self.map.addObject(drop_obj[2].name, drop_obj[2].type, drop_obj[0], drop_obj[1])

        new_repo = [obj for obj in self.repo if obj.id != drop_obj.id]
        self.repo = new_repo


class Mine(Object):
    def init(self, p, d, k):
        self.prox = p
        self.dmg = d
        self.itr = k
        self.run()
    
    def run(self):
        time.sleep(0.1)
        for i in range(self.itr):
            for i, tpl in range(len(Map.objects_list)):
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            for obj in Map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    obj[2].health -= self.dmg

class Freezer(Object):
    def init(self, p, d, k):
        self.prox = p
        self.stun = d
        self.itr = k
        self.run()
    
    def run(self):
        time.sleep(0.1)
        for i in range(self.itr):
            for i, tpl in range(len(Map.objects_list)):
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            for obj in Map.query(x, y, self.prox):
                if(obj[2].type == "Player"):
                    obj[2].stun(self.stun)

class Health(Object):
    def init(self, m, inf):
        self.health = m
        self.cap = inf
        self.run()
    
    def run(self):
        while(self.inf):
            cond = True
            while(cond):
                for i, tpl in range(len(Map.objects_list)):
                        if tpl[2].id == self.id:
                            x = tpl[0]
                            y = tpl[1]
                for obj in Map.query(x, y, 3):
                    if(obj[2].type == "Player"):
                        obj[2].health += self.health
                        cond = False


""" obj1 = Object("Player1","Player")
obj2 = Object("StrongMine", "Mine")

print(obj1.id)
print(obj2.id) """