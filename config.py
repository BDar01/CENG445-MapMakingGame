from game import *

MAPS = {
    "arena": {
        "type": "Arena",
        "image":"BackgroundImage1.jpg", 
        "playervision": 2000, 
        "playerh": 100, 
        "playerrepo": [("Mine", 3, 20, 500000), ("Freezer", 1, 10, 500000)], 
        "objects": [(20, 45, Mine(None, 7, 30, 10000)), (150, 285, Freezer(None, 5, 4, 10000))]
    },
    "labyrinth": {
        "type": "Labyrinth",
        "image":"BackgroundImage2.jpg", 
        "playervision": 3000, 
        "playerh": 120, 
        "playerrepo": [("Mine", 6, 25, 10000), ("Freezer", 10, 3, 10000)], 
        "objects": [(28, 333, Mine(None, 10, 50, 8000)), (800, 333,  Freezer(None, 3, 10, 8000))]
    }
}