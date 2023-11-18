from map import Map

class Object:
    id = -1

    def __init__(self, name, type):
        Object.id += 1

        self.name = name
        self.type = type
        self.id = Object.id
        
class Player(Object):

    def __init__(self, user, team, health, repo, map):
        self.user = user
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

        if(direction == "NW"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] - 1, tpl[1] + 1, tpl[2])
        
        if(direction == "N"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0], tpl[1] + 1, tpl[2])

        if(direction == "NE"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1] + 1, tpl[2])

        if(direction == "E"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1], tpl[2])

        if(direction == "SE"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] + 1, tpl[1] - 1, tpl[2])

        if(direction == "S"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0], tpl[1] - 1, tpl[2])

        if(direction == "SW"):
            for i, tpl in range(object_list_length):
                if tpl[2].id == self.id:
                    objects_list[i] = (tpl[0] - 1, tpl[1] - 1, tpl[2])

    def updateBackgroundImage(self, direction):
        return
    
    def move(self, direction):

        self.updatePositionOfPlayer(self, direction)
        self.updateBackgroundImage(self, direction)

    def drop(self, objecttype):

        available_objects = [obj for obj in self.repo if obj[0] == objecttype]
        if(len(available_objects) > 0):
            return
            











""" obj1 = Object("Player1","Player")
obj2 = Object("StrongMine", "Mine")

print(obj1.id)
print(obj2.id) """