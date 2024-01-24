from game import *

MAPS = {
    "arena": {
        "type": "Arena",
        "image":"BackgroundImage1.jpg", 
        "playervision": 50, 
        "playerh": 100, 
        "playerrepo": [("Mine", 10, 50, 1000000), ("Mine", 10, 50, 1000000), ("Mine", 10, 50, 1000000), ("Freezer", 20, 8, 500000), ("Health", 20, False)], 
        "objects": [(200, 300, Mine(None, 7, 30, 1500000, None, -1)), (20, 45, Mine(None, 7, 30, 1500000, None, -1)), (150, 285, Freezer(None, 5, 4, 900000, None, -1))]
    },
    "labyrinth": {
        "type": "Labyrinth",
        "image":"BackgroundImage2.jpg", 
        "playervision": 50, 
        "playerh": 120, 
        "playerrepo": [("Mine", 15, 30, 2000000), ("Mine", 15, 30, 2000000), ("Mine", 15, 30, 2000000), ("Mine", 15, 30, 2000000), ("Freezer", 18, 10, 800000)], 
        "objects": [(480, 645, Mine(None, 7, 30, 1000000, None, -1)), (28, 333, Mine(None, 10, 20, 4000000, None, -1)), (800, 333,  Freezer(None, 15, 10, 800000, None, -1)), (30, 100, Health(10, -1, None, -1))]
    }
}