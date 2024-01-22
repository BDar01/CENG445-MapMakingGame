from game import *

MAPS = {
    "arena": {
        "type": "Arena",
        "image":"BackgroundImage1.jpg", 
        "playervision": 2000, 
        "playerh": 100, 
        "playerrepo": [("Mine", 10, 50, 100000), ("Mine", 10, 50, 100000), ("Mine", 10, 50, 100000), ("Freezer", 20, 8, 150000), ("Health", 20, False)], 
        "objects": [(20, 45, Mine(None, 12, 30, 500000)), (150, 285, Freezer(None, 25, 20, 600000))]
    },
    "labyrinth": {
        "type": "Labyrinth",
        "image":"BackgroundImage2.jpg", 
        "playervision": 3000, 
        "playerh": 120, 
        "playerrepo": [("Mine", 15, 30, 100000), ("Mine", 15, 30, 100000), ("Mine", 15, 30, 100000), ("Mine", 15, 30, 100000), ("Freezer", 18, 10, 300000)], 
        "objects": [(28, 333, Mine(None, 10, 20, 400000)), (800, 333,  Freezer(None, 15, 10, 800000)), (30, 100, Health(10, True))]
    }
}