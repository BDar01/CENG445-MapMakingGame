from game import *

separator = "****************"

mineObject = Mine("Mine1", 7, 30, 1000)    
#healthObject = Health("Health1", 20, False) If we add this object, since we didn't implement the threads functionality, it will run forever and the program won't work.
#healthObject2 = Health("Health2", 20, True) If we add this object, since we didn't implement the threads functionality, it will run forever and the program won't work.
freezerObject = Freezer("Freezer1", 5, 4, 1000)

config1 = {"image":"BackgroundImage1.jpg", 
           "playervision": 10, 
           "playerh": 100, 
           "playerrepo": [("Mine", "Mine Repo1", 3, 20, 1000), ("Freezer", "Freezer Repo1", 3, 5, 10000)], 
           "objects": [(2, 3, mineObject), (10, 10, freezerObject)]
        }
size = (612, 408)
map1 = Map("Map1", size, config1)
print("Map Created. Here it is:")
print("Line 1:", map1) #Line 1, Here we can see that map instantiated properly.
print(separator)

player = map1.join("Baran", "Red Team")
print("Baran joined")
print("Line 2:", map1) #Line 2, Here we can see that Player is added to the objects of the map, which means the player properly joined the map.
print(separator)

print("Line 3:", player)
print(separator)
player.drop("Mine")
print(map1)
print(player.map.teams[player.team])
print("Line 4:", player) #By looking to this line (comparing it with Line 3) we can see it dropped the Mine and since the mine is in our posiiton and we didn't go away before it activates, it decreased our health value.ü

player.move("E")
print("Line 5:", "Global View Update", ([obj for obj in player.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][0], 
        [obj for obj in player.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the global map has been affected.
print("Line 6:", "Local View Update", ([obj for obj in player.map.teams[player.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][0], 
        [obj for obj in player.map.teams[player.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the local map has been affected.
player.move("W")
player.move("NE")
player.move("NE")
player.move("SW")
player.move("S")
player.move("N")
player.move("SE") 
print(separator)
print("Line 6:", ([obj for obj in player.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][0], 
        [obj for obj in player.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][1])) #Expected to be in (2,0)
player.move("S") #Expected to not change. (checking bounds)
print(separator)
print("Line 7:", ([obj for obj in map1.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][0], 
        [obj for obj in map1.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player.id][0][1])) #Expected to be in (2,0)

player.drop("Freezer")
print("Line 8:", player) #Freezer dropped, freezed for a time interval, since we didn't move away before it gets activated.

##### Will create more test cases for the demo ####



