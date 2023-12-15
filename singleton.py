from game import *

def singleton(cls):
    _instances = {}
    def getinstance():
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]
    return getinstance

@singleton
class UserFactory(object):
    user_list = {}

    def new(self, username, email, fullname, passwd):
        user = User(username, email, fullname, passwd)
        UserFactory().user_list[user.user_id] = user
        return user
    
    def new_from_load(self, user_id, username, email, fullname, pwd_hash, token):
        user = User(username, email, fullname, "")
        user.user_id = user_id
        user.pwd_hash = pwd_hash
        user.token = token
        UserFactory().user_list[user.user_id] = user

    def get(self, id):
        return self.user_list[id]

@singleton
class MapFactory(object):
    map_list = {}

    def new(self, name, size, config):
        map = Map(name, size, config)
        MapFactory().map_list[map.map_id] = map
        return map
    
    def new_from_load(self, name, size, config, map_id):
        map = Map(name, size, config)
        map.map_id = map_id
        MapFactory().map_list[map.map_id] = map
        return map

    def get(self, id):
        return self.map_list[id]

