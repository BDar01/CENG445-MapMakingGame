from game import *

MAPS = {
    "arena": {"image":"BackgroundImage1.jpg", 
        "playervision": 10, 
        "playerh": 100, 
        "playerrepo": [("Mine", 3, 20, 1000), ("Freezer", 1, 5, 10000)], 
        "objects": [(2, 3, Mine(7, 30, 1000)), (10, 10, Freezer(5, 4, 1000))]
    },
    "labyrinth": {
        "image":"BackgroundImage2.jpg", 
        "playervision": 8, 
        "playerh": 120, 
        "playerrepo": [("Mine", 6, 25, 1000), ("Freezer", 10, 3, 5000)], 
        "objects": [(2, 3, Mine(10, 50, 800) ), (10, 10,  Freezer(3, 6, 500))]
    }
}