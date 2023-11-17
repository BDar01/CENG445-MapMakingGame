# CENG445-MapMakingGame

CEng 445 Spring 2023 Projects Class Interface
The following class descriptions may not be final or not the best way to implement the projects. 
You can modify the arguments, add new methods as long as you can justify it.

In the projects, abbreviation CRUD implies implementation of the following
methods:
Method: Description
constructor(...): Create a new instance of the class from arguments

get(): Read. Return a textual representation of the item,
you can use JSON like representation or simply records separated by punctuation (CSV)

update(**kw): Update. Update the current item with new values.
Updated parameters are given as keyword arguments. Other parameters remain the same

delete(): Delete. Delete the item.

In all projects, edited objects are maintained in global structures or singleton
catalogue object of your choice. Each constructed object will be assigned a
unique id and getid(...) method returns it. Users can call attach(id)
method to get the object with given id and detach() method on object to
release (name and paramater may change based on the topic). Depending on
the project, this may result in getting notifications and not getting notifications.

Also listobject() class methods give a list of objects to attach with their
names.

In all projects, users and authentication are required. However it is delayed
until the second phase. In the second phase, the following interface should be
implemented:

User class:

Method: Description
constructor(username, email, fullname, passwd): Create the user with a password

CRUD: methods in addition to constructor

auth(plainpass): Check if supplied password matches user password

login(): Start a session for the user, return a random token to be used during the session

checksession(token): Check if the token is valid, returned by the last login

logout(): End the session invalidating the token

Use hashlib for storing the passwords. Do not store plain passwords. Use uuid
module when you need to generate unique ids.

For the first phase, just implement a method switchuser(userid) to switch
to an arbitrary user id, to show multi user functionality. Each created object
will have current user is registered as implicity owner and will be returned in
outputs (ie. get() methods).

There will be no notification in the first phase.

Also you do not need to implement any persistency in this phase. All objects
are lost when program stops.


Map Making Game
 
In this project users play on a global Map object. System has a repository of
maps and user joins to one of them, releasing the previously joined map. The
joined map contains all data of all players. Map class is also used for keeping
track of the teams view of the map. For each team a Map is created and players
update their local views on this objects so all team members can see it. A map
has a background image and a list of associated objects. A team map starts
from blank background and as discovered it contains patches from original map.

Map has the following members:

Method: Description
constructor(name, size, config): Creates a map with given dimensions
(width,height) tuple as size. The background image is given as a file path in the config.
Background is blank if image is not provided

addObject(name, type, x, y): Adds an object on the 2D grid. type is explained below.

removeObject(id): remove the object with id

listObjects(id): return all objects in the map with (id, name, type, x, y) tuple as an iterator.

getimage(x,y,r): get the background image defined by the rectangle. Rectangle is defined as a 2*r by 2*r
square centered at x,y

setimage(x,y,r, image): set the background image patch at the rectangle.

query(x,y,r): return all objects in a rectangular area as an iterator. Area is defined as a 2*r by 2*r square
centered at x,y

join(player,team): A player joins the game of the global map. team is a string for the team name. If team name
exists, user is associated with the Map of the team, otherwise the Map is created.

leave(player,team): A player leaves the game. Users have to call join() before leaving the map and leave()
existing games before joining again.

teammap(team): Returns the team map of the given team name

The objects on a map can have the following types:
• A Player is an object created per user. As user joins a map, it is inserted
at default position (0,0). It can move across the map. Players have a
health value and a collection of objects that they can insert at their current
position. When health gets to 0, player leaves the map.
• A Mine is a bomb trigerred when someone gets close to a proximity p. Mine
starts when it is left on a map. It runs a loop of wait for a while to load,
then wait until someone gets in the range, then explode. After running
for k iterations, Mine is deleted, it disappears. When mine explodes, the
players in proximity gets their health reduced with amount d.p, d and k
are given as constructor parameters.
• A Health increases the health of players to parameter m when they get as
close as 3 pixels. Some Health objects have infite capacity and remains
forever in the map. Some of them are carried by users and disappear
after being used. Players throw them on 5 pixels away so they can be
used by other users. The boolean constructor parameter inf defines this
behaviour.
• A Freezer works like a Mine but stunns the player for d seconds.

The config parameter of Map constructor may contain the values in a dictionary:
• image: file path given the background image of the map. It should match
the dimensions of the Map.
• playervision: default size of the square area that a user can query and
get image of.
• playerh: default player health assigned when a player joins the map.
• playerrepo: list of items given to player when s/he joins the map. It is
a list of tuples as (cls, p0, p1, p2,...). cls is the type of the object
and following values are constructor parameters.
• objects: list of items initially put on the map. It is a list of triples as
(x,y,object). Objects are constructed and put into this list.

Player instance is created and returned by Map.join() when a user joins a Map.
The class will have the following methods:

Method: Description
constructor(user, team, health, repo, map): Default values are assigned based on the
configuration of the map
move(DIRECTION): Player moves on a direction (‘N,NW,W,SW,…’) on the map. Each move will result on a query
and image update of the team map.
drop(objecttype): Player drops and object in its repository at the current position

When the players of different teams meet on a point, a competition or fight will
take place. The rules are left for the second phase.

In the following phases, the objects in the Map will work in different threads
to implement the timing and they are going to synchronize on proximity based
events. For this phase, there will be no timing, proximity triggers and notifications.
