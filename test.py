from game import *

separator = "****************"

mineObject = Mine("Mine1", 7, 30, 1000) 
mineObject2 = Mine("Mine2", 10, 50, 800) 
#healthObject = Health("Health1", 20, False) If we add this object, since we didn't implement the threads functionality, it will run forever and the program won't work.
#healthObject2 = Health("Health2", 20, True) If we add this object, since we didn't implement the threads functionality, it will run forever and the program won't work.
freezerObject = Freezer("Freezer1", 5, 4, 1000)
freezerObject2 = Freezer("Freezer2", 3, 6, 500)

config1 = {"image":"BackgroundImage1.jpg", 
           "playervision": 10, 
           "playerh": 100, 
           "playerrepo": [("Mine", "Mine Repo1", 3, 20, 1000), ("Freezer", "Freezer Repo1", 1, 5, 10000)], 
           "objects": [(2, 3, mineObject), (10, 10, freezerObject)]
        }
size1 = (612, 408)
map1 = Map("Map1", size1, config1)
print("Map 1 Created. Here it is:")
print("Map 1 Line 1:", map1) #Map 1 Line 1, Here we can see that map 1 is instantiated properly.
print(separator)

config2 = {"image":"BackgroundImage2.jpg", 
           "playervision": 8, 
           "playerh": 120, 
           "playerrepo": [("Mine", "Mine Repo2", 6, 25, 1000), ("Freezer", "Freezer Repo2", 10, 3, 5000)], 
           "objects": [(2, 3, mineObject2), (10, 10, freezerObject2)]
        }
size2 = (256, 256)
map2 = Map("Map2", size2, config2)
print("Map 2 Created. Here it is:")
print("Map 2 Line 1:", map2) #Map 2 Line 1, Here we can see that map 2 is instantiated properly.
print(separator)

player1 = map1.join("Baran", "Red Team")
print("Baran joined")
print("Map 1 Line 2:", map1) #Map 1 Line 2, Here we can see that Player 1 is added to the objects of the map 1, which means the player properly joined the map.
print(separator)

player1b = map1.join("Dar", "Red Team")
print("Dar joined")
print("Map 1 Line 3:", map1) #Map 1 Line 3, Here we can see that Player 1b is added to the objects of the map 1, which means the player properly joined the map.
print(separator)

player2 = map2.join("Basim", "Blue Team")
print("Basim joined")
print("Map 2 Line 2:", map2) #Map 2 Line 2, Here we can see that Player 2 is added to the objects of the map 2, which means the player properly joined the map.
print(separator)

print("Map 1 Line 4:", player1)
print(separator)
print("Map 1 Line 5:", player1b)
print(separator)
player1.drop("Mine")
print(map1)
print(player1.map.teams[player1.team])
print("Map 1 Line 6:", player1) #By looking to Map 1 line 6 and 7 (comparing it with Map 1 Line 4 and 5) we can see it dropped the Mine and since the mine is in our posiiton and we didn't go away before it activates, it decreased our health value.
print(separator)
print("Map 1 Line 7:", player1b)
print(separator)

player1b.drop("Mine")
print(map1)
print(player1b.map.teams[player1b.team])
print("Map 1 Line 8:", player1) #By looking to Map 1 line 8 and 9 (comparing it with Map 1 Line 6 and 7) we can see it dropped the Mine and since the mine is in our posiiton and we didn't go away before it activates, it decreased our health value.
print(separator)
print("Map 1 Line 9", player1b)
print(separator)

print("Map 2 Line 3:", player2)
print(separator)
player2.drop("Mine")
print(map2)
print(player2.map.teams[player2.team])
print("Map 2 Line 4:", player2) #By looking to this line (comparing it with Map 2 Line 3) we can see it dropped the Mine and since the mine is in our posiiton and we didn't go away before it activates, it decreased our health value.


player1.move("E")
print("Map 1 Line 10:", "Global View Update", ([obj for obj in player1.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][0], 
        [obj for obj in player1.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the global map has been affected.
print("Map 1 Line 11:", "Local View Update", ([obj for obj in player1.map.teams[player1.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][0], 
        [obj for obj in player1.map.teams[player1.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the local map has been affected.
player1.move("W")
player1.move("NE")
player1.move("NE")
player1.move("SW")
player1.move("S")
player1.move("N")
player1.move("SE") 
print(separator)
print("Map 1 Line 12:", ([obj for obj in player1.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][0], 
        [obj for obj in player1.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][1])) #Expected to be in (2,0)
player1.move("S") #Expected to not change. (checking bounds)
print(separator)
print("Map 1 Line 13:", ([obj for obj in map1.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][0], 
        [obj for obj in map1.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player1.id][0][1])) #Expected to be in (2,0)

player1.drop("Freezer")
print("Map 1 Line 14", player1b) #Not affected by Freezer dropped by Player 1, as Player 1b is out of range
print(separator)
print("Map 1 Line 15:", player1) #Freezer dropped, freezed for a time interval, since we didn't move away before it gets activated.
print(separator)

player2.move("E")
print("Map 2 Line 5:", "Global View Update", ([obj for obj in player2.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][0], 
        [obj for obj in player2.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the global map has been affected.
print("Map 2 Line 6:", "Local View Update", ([obj for obj in player2.map.teams[player2.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][0], 
        [obj for obj in player2.map.teams[player2.team].objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][1])) #By looking to this line we can see the player moved as it supposed to and the local map has been affected.
player2.move("N")
player2.move("NW")
player2.move("NE")
player2.move("E")
player2.move("S")
player2.move("SE")
player2.move("SW") 
print(separator)
print("Map 2 Line 6:", ([obj for obj in player2.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][0], 
        [obj for obj in player2.map.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][1])) #Expected to be in (2,0)
player2.move("S") #Expected to not change. (checking bounds)
print(separator)
print("Map 2 Line 7:", ([obj for obj in map2.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][0], 
        [obj for obj in map2.objects_list if obj[2].__class__.__name__ == "Player" and obj[2].id == player2.id][0][1])) #Expected to be in (2,0)

player2.drop("Freezer")
print("Map 2 Line 8:", player2) #Freezer dropped, freezed for a time interval, since we didn't move away before it gets activated.

##### Will create more test cases for the demo ####

