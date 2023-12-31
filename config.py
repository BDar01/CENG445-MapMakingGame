from game import *

MAPS = {
    "arena": {
        "type": "Arena",
        "image":"BackgroundImage1.jpg", 
        "playervision": 2000, 
        "playerh": 100, 
        "playerrepo": [("Mine", 3, 20, 1000), ("Freezer", 1, 5, 10000)], 
        "objects": [(20, 45, Mine(7, 30, 1000)), (150, 285, Freezer(5, 4, 1000))]
    },
    "labyrinth": {
        "type": "Labyrinth",
        "image":"BackgroundImage2.jpg", 
        "playervision": 3000, 
        "playerh": 120, 
        "playerrepo": [("Mine", 6, 25, 1000), ("Freezer", 10, 3, 5000)], 
        "objects": [(28, 333, Mine(10, 50, 800) ), (800, 333,  Freezer(3, 6, 500))]
    }
}