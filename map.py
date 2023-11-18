from object import *
class Map:
    def __init__(self, name, size, config):
        self.name = name
        self.size = size
        self.config = config
        self.objects_list = config.objects

    def addObject(self, name, type, x, y):
        object = Object(name, type)
        self.objects_list.append((x,y,object))
    
    def removeObject(self, id):
        new_objects_list = [obj for obj in self.objects_list if obj.id != id]
        self.objects_list = new_objects_list

    def listObjects(self):
        output = [(obj[2].id, obj[2].name, obj[2].type, obj[0], obj[1]) for obj in self.objects_list]
        return output
    
    def getimage(self, x, y, r):
        return
    
    def setimage(self, x, y, r, image):
        return
    
    def query(x, y, r):
        return
    
    def join(player, team):
        return

    def leave(player, team):
        return
    
    def teammap(team):
        return
    
    
