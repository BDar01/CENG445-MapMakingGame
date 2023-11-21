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
        super.__init__(user, "Player")
        self.team = team
        self.health = health
        self.repo = repo
        self.map = map

    def updatePositionOfPlayer(self, direction):
        objects_list = Map.objects_list # need global map
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
        for i, tpl in range(len(Map.objects_list)): # need global map
            if tpl[2].id == self.id:
                x = tpl[0]
                y = tpl[1]
        self.map.bg_img.setimage(x, y, 0, Map.getimage(x,y,0)) # need global map
    
    def move(self, direction):

        self.updatePositionOfPlayer(direction)
        self.updateBackgroundImage(direction)
        # need to query
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
        if(drop_obj):
            for i, tpl in range(len(Map.objects_list)): # need global map
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            if (drop_obj[0] == "Health"):
                self.map.objects_list.append((x,y,Health(drop_obj[1],drop_obj[2],drop_obj[3])))
            if (drop_obj[0] == "Mine"):
                self.map.objects_list.append((x,y,Mine(drop_obj[1],drop_obj[2],drop_obj[3], drop_obj[4])))
            if (drop_obj[0] == "Freezer"):
                self.map.objects_list.append((x,y,Freezer(drop_obj[1],drop_obj[2],drop_obj[3], drop_obj[4])))

        new_repo = [obj for obj in self.repo if obj.id != drop_obj.id]
        self.repo = new_repo


class Mine(Object):
    def __init__(self, name, p, d, k):
        super.__init__(name, "Mine")
        self.prox = p
        self.dmg = d
        self.itr = k
        self.run()
    
    def run(self):
        time.sleep(0.1)
        for i in range(self.itr):
            for i, tpl in range(len(Map.objects_list)): # need global map
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            for obj in Map.query(x, y, self.prox): # need global map
                if(obj[2].type == "Player"):
                    obj[2].health -= self.dmg

class Freezer(Object):
    def __init__(self, name, p, d, k):
        super.__init__(name, "Freezer")
        self.prox = p
        self.stun = d
        self.itr = k
        self.run()
    
    def run(self):
        time.sleep(0.1)
        for i in range(self.itr):
            for i, tpl in range(len(Map.objects_list)): # need global map
                    if tpl[2].id == self.id:
                        x = tpl[0]
                        y = tpl[1]
            for obj in Map.query(x, y, self.prox): # need global map
                if(obj[2].type == "Player"):
                    obj[2].stun(self.stun)

class Health(Object):
    def __init__(self, name, m, inf):
        super.__init__(name, "Health")
        self.health = m
        self.cap = inf
        self.run()
    
    def run(self):
        while(self.inf):
            cond = True
            while(cond):
                for i, tpl in range(len(Map.objects_list)): # need global map
                        if tpl[2].id == self.id:
                            x = tpl[0]
                            y = tpl[1]
                for obj in Map.query(x, y, 3): # need global map
                    if(obj[2].type == "Player"):
                        obj[2].health += self.health
                        cond = False


""" obj1 = Object("Player1","Player")
obj2 = Object("StrongMine", "Mine")

print(obj1.id)
print(obj2.id) """