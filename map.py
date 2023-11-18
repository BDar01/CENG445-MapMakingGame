from object import *
import cv2 as cv
import numpy as np

class Map:
    def __init__(self, name, size, config):
        self.name = name
        self.size = size
        self.config = config
        self.objects_list = config.objects

        bg_img = cv.imread(config.image)
        if(bg_img and bg_img.shape[0] == size[1] and bg_img.shape[1] == size[0]):
            self.background_image = bg_img
        else:
            self.background_image = np.zeros((size[1],size[0],3), np.uint8)

    def addObject(self, name, type, x, y):
        object = Object(name, type)
        self.objects_list.append((x,y,object))
    
    def removeObject(self, id):
        new_objects_list = [obj for obj in self.objects_list if obj.id != id]
        self.objects_list = new_objects_list

    def listObjects(self):
        output = [(obj[2].id, obj[2].name, obj[2].type, obj[0], obj[1]) for obj in self.objects_list]
        return iter(output)
    
    def getimage(self, x, y, r):
        bg_image = np.zeros((2*r,2*r,3), np.uint8)

        for i in range(-r, r+1):
            for j in range(-r, r+1):
                for k in range(3):
                    bg_image[i+r][j+r][k] = self.background_image[i+x][j+y][k]
        return bg_image
    
    def setimage(self, x, y, r, image):
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                for k in range(3):
                    self.background_image[i+x][j+y][k] = image[i+r][j+r][k]
    
    def query(self, x, y, r):
        new_objects_list = [obj for obj in self.objects_list if (r-x <= obj[0] <= r+x) and (r-y <= obj[0] <= r+y)]
        return iter(new_objects_list)
    
    def join(player, team):
        return

    def leave(player, team):
        return
    
    def teammap(team):
        return
    
    
