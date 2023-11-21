from map import *

mineObject = Mine("Mine1", 7, 30, 1000)    
healthObject = Health("Health1", 20, False)
healthObject2 = Health("Health2", 20, True)
freezerObject = Freezer("Freezer1", 5, 4, 1000)

config1 = {"image":"BackgroundImage1.jpg", 
           "playervision": 10, 
           "playerh": 100, 
           "playerrepo": [("Mine", 3, 20, 1000), ("Freezer", 3, 5, 10000)], 
           "objects": [(2, 3, mineObject), (10, 10, freezerObject), (-2, -5, healthObject), (-10, -10, healthObject2)]
        }
size = (612, 408)
map1 = Map("Map1 (Global)", size, config1)
print("Map Created. Here it is:")
print(map1)


map1.join("Baran", "Red Team")
print("Baran joined")
print(map1)