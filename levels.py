"""Levels in game."""
from game_objects import GameObject, Door, Container, switch_boolean_state, relocate_item, find_item_place, get_object
from place import Place, MazeGrid
import command
LEVELS = []
class Maze:
    """A maze is just places in a grid, some accessible, some inaccessible.
    
    Attributes:
        mazeMap (list): Map of maze. This is a list of strings representing rows, with each character being
                       either '.' (a blank space) or '#' (a wall).
        places (dict): Represents each coordinate of the maze. Mapped with a tuple of 2 integers x, y is
                       a place.MazeGrid
        player (player.Player): The user playing the game, still in this maze.
        height (int): The height of the maze
        length (int): The length of the maze
    
    Methods:
        __getitem__(coord): 
            Returns the place object at the coordinate in the maze.
        
        move_player_towards(direction):
            Moves the player in the direction of direction, if possible.
    """
    def __init__(self, mazeMap, player):
        self.mazeMap = mazeMap
        self.places = {}
        self.player = player
        self.height = len(mazeMap)
        self.length = len(mazeMap[0])
        for i in range(self.height):
            for j in range(self.length):
                direction_objects = {}
                for direction in ['left', 'right', 'up', 'down']:
                    direction_object = GameObject(direction)\
                                       .change_description("Calling `move direction` moves the player towards that direction.")\
                                       .add_command('move', "Moves the player towards this direction.", successMsg=None,
                                                    result_success=lambda direction=direction: self.move_player_towards(direction))
                    direction_objects[direction] = direction_object
                self.places[(i, j)] = MazeGrid(i, j, objects=direction_objects, reachable=mazeMap[i][j] == '.')

    def __getitem__(self, coord):
        return self.places[tuple(coord)]

    def move_player_towards(self, direction_word):
        """Moves the player in the direction of direction, if possible.
        
        Args:
            direction_word (str): Direction where the player wants to move. Must be either 'left', 'right',
                                  'up' or 'down'.
        Returns:
            None
        """
        if direction_word == 'left':
            newx, newy = self.player.place.x, self.player.place.y - 1
        elif direction_word == 'right':
            newx, newy = self.player.place.x, self.player.place.y + 1
        elif direction_word == 'up':
            newx, newy = self.player.place.x - 1, self.player.place.y
        elif direction_word == 'down':
            newx, newy = self.player.place.x + 1, self.player.place.y
        if newx < 0 or newx >= self.height or newy < 0 or newy >= self.length or self.mazeMap[newx][newy] != '.':
            print("Sorry, that's a wall. You cannot travel there.")
        else:
            self.player.set_current_place(self.places[(newx, newy)])
            self.places[(newx, newy)].describe_place()

    
class Level:
    """A level of the game. Each level contains many places.
    
    Attributes:
        levelNum (int): The level number.
        places (dict): Places in this level. The dictionary maps the place's names to the place object itself.
        placesNames (list): List of names of the places.
        startPlace (any): The name of the player's starting place. Must be an existing key in the places dictionary.
        msgOnEnter (str): Message to be printed when the player starts this level. Defaults None, and so all the places 
                          in the level will be printed to the console.

    Methods:
        show_introduction(): 
            Prints introduction message to the console.
        show_all_places():
            Prints all the places in this level to the console.
    """

    def __init__(self, levelNum, places, startPlace, msgOnEnter=None):
        """Initialise escape room level with given game objects."""
        self.levelNum = levelNum
        self.places = places
        self.placesNames = [placeName for placeName in self.places if isinstance(placeName, str)]
        self.startPlace = startPlace
        self.msgOnEnter = msgOnEnter

    def show_introduction(self):
        """Prints introduction `self.msgOnEnter` to the screen when player first starts this level. If `self.msgOnEnter` 
        is None, prints default message."""
        if self.msgOnEnter is None:
            self.show_all_places()
        else:
            print(self.msgOnEnter)

    def show_all_places(self):
        """Prints all the places in this level to the console."""
        print("In this level, there are %d place(s) you can go: %s." % (len(self.places), ', '.join(self.placesNames)))

def completed_level(player, level):
    """A level had been completed. Start a new level if possible.
    
    Args:
        player (Player.player): The current user who had completed this level.
        level (int): The level which the player passed. Used here only for clarity.
    Returns:
        None
    """
    player.advance_level()
    try:
        LEVELS[player.level - 1]
    except IndexError:
        print("Congratulations! You escaped all the rooms and won the game!")
        return
    play_level(level=player.level, player=player)

def make_levels(player):
    """Make levels.
    
    Args:
        player (player.Player): The current user playing the game.
    Returns:
        None
    Side Effects:
        Changes global variable "LEVELS" by populating it with the actual game level maps.
    """
    global LEVELS

    # This is intended to be a long function.
    # Populate levels with 'lvl(lvlNum)_places' and 'lvl(lvlNum)_(place)_objects'
    # Create all the objects inside the objects dictionary, and all the places in the places dictionary.
    # Note that a different variables needs to be used for every different level due to closures being used, 
    # which freely changes the variables.

    # Level 1
    lvl1_places = {}

    # Populate bedroom.
    lvl1_bedroom_objects = {}
    lvl1_bedroom_objects['door'] = Door('door', opened=False,
                                        closedMsg="It's a exit door locked with `door.lock`.",
                                        openMsg="You may open the door and exit now.")\
                                   .add_command('open', "Opens door if door is unlocked",
                                                successMsg="Door is opened! You completed Level 1! Good job!",
                                                failMsg="Door is locked.", req='unlocked door.lock',
                                                result_success=lambda: completed_level(player, 1))\
                                   .lock_with_key('bed.key', lvl1_bedroom_objects, player)

    lvl1_bedroom_objects['scissors'] = GameObject('scissors')\
                                       .set_collectable()

    lvl1_bedroom_objects['bed'] = Container('bed', contains=['bed.key'], 
                                            closedDescription="There seemed to be something hard inside this bed. "
                                                              "Maybe you \nmay try cutting it?")\
                                  .add_command('cut', "Cut the bed.",
                                               successMsg="You cut the bed with the scissors.",
                                               failMsg="You need a tool...",
                                               req='collected scissors',
                                               result_success=lambda: lvl1_bedroom_objects['bed']\
                                                                      .open(openedIn=lvl1_places["bedroom"]))
    
    lvl1_bedroom_objects['bed.key'] = GameObject('bed.key')\
                                      .set_collectable()\
                                      .set_accessibility(False)

    lvl1_places["bedroom"] = Place("bedroom", objects=lvl1_bedroom_objects)

    LEVELS.append(Level(1, places=lvl1_places, startPlace="bedroom"))

    # Level 2
    lvl2_places = {}

    # Living room
    lvl2_living_room_objects = {}
    lvl2_living_room_objects['drawer'] = Container('drawer', contains=['drawer.key', 'drawer.paper'])\
                                         .add_command('open', 'Opens the drawer', 
                                                      successMsg="The drawer is open. "
                                                                 "There is something interesting inside.", 
                                                       result_success=lambda: lvl2_living_room_objects['drawer']\
                                                                              .open(lvl2_places['living room']))

    lvl2_living_room_objects['drawer.key'] = GameObject('drawer.key')\
                                             .set_collectable()\
                                             .set_accessibility(False)

    lvl2_living_room_objects['drawer.paper'] = GameObject('drawer.paper')\
                                               .add_command('read', "Reads message.", 
                                                            successMsg="Blue 2, Green 5, Red 8, Yellow 4")\
                                               .set_accessibility(False)

    lvl2_living_room_objects['table'] = Container('table', contains=['table.paper'], isOpen=True)

    lvl2_living_room_objects['table.paper'] = GameObject('table.paper')\
                                              .add_command('read', "Reads message.", 
                                                           successMsg="Yellow, Green, Red, Blue")

    lvl2_living_room_objects['table'].add_included_item(lvl2_living_room_objects['table.paper'])

    lvl2_living_room_objects['kitchen door'] = Door('kitchen door', opened=False, 
                                                    closedMsg="Kitchen door is locked with kitchen_door.lock.", 
                                                    openMsg="Type `enter kitchen` to enter kitchen.")\
                                               .add_command('open', "Opens the door.", 
                                                            successMsg="Door is opened.", failMsg="Door is locked.",
                                                            req="unlocked kitchen door.lock", 
                                                            result_success=lambda: lvl2_places['kitchen']\
                                                                                   .set_reachable(True))\
                                               .lock_with_password("4582",objects=lvl2_living_room_objects, 
                                                                   player=player)
    
    lvl2_places['living room'] = Place("living room", objects=lvl2_living_room_objects)
    
    # Kitchen
    lvl2_kitchen_objects = {}

    lvl2_kitchen_objects['window'] = GameObject("window")\
                                     .change_description("You look out of the window. You realise that it is "
                                                         "safe to jump out of the window, as this is a one-storey "
                                                         "house. However, the window is locked.")\
                                     .add_command('break', 'Breaks window with a tool.', 
                                                  successMsg="You broke through the window and escaped.\n"
                                                             "You completed Level 2! Way to go!", 
                                                  failMsg="You need a tool...", req="collected drawer.safe.hammer", 
                                                  result_success=lambda: completed_level(player, 2))

    lvl2_kitchen_objects['drawer'] = Container("drawer", contains=["drawer.safe"], 
                                               closedDescription="`drawer` is locked with `drawer.lock`.")\
                                     .add_command("open", "Opens the kitchen drawer.", 
                                                  successMsg="There is something interesting inside.", 
                                                  failMsg="Drawer is locked.", req="collected drawer.key", 
                                                  result_success=lambda: lvl2_kitchen_objects['drawer']\
                                                                         .open(lvl2_places['kitchen']))\
                                     .lock_with_key('drawer.key', objects=lvl2_kitchen_objects, player=player)

    lvl2_kitchen_objects['drawer.safe'] = Container("drawer.safe", contains=["drawer.safe.hammer"], 
                                                    closedDescription="This is a special safe. You need to play"
                                                    " a Hangman game to unlock its lock (`drawer.safe.lock`).")\
                                          .add_command("open", "Open the safe.", 
                                                       successMsg="Wow! A useful tool! Examine to find out more!", 
                                                       failMsg="The safe is locked.", req="unlocked drawer.safe.lock",
                                                       result_success=lambda: lvl2_kitchen_objects['drawer.safe']\
                                                                              .open(lvl2_places['kitchen']))\
                                          .lock_with_game("Hangman", objects=lvl2_kitchen_objects, player=player)\
                                          .set_accessibility(False)

    lvl2_kitchen_objects['drawer.safe.hammer'] = GameObject('drawer.safe.hammer')\
                                                 .set_collectable()\
                                                 .set_accessibility(False)
    
    lvl2_places['kitchen'] = Place("kitchen", objects=lvl2_kitchen_objects, reachable=False)

    LEVELS.append(Level(2, places=lvl2_places, startPlace="living room"))

    lvl3_places = {}

    lvl3_backyard_objects = {}
    lvl3_backyard_objects['gate'] = Door('gate', opened=False, closedMsg="Door is locked with gate.lock.",
                                         openedMsg="Gate is open. You may exit now.")\
                                    .add_command("open", "Opens the gate.", 
                                                 successMsg="You opened the gate.\nWell done, you conquered Level 3!",
                                                 failMsg="Gate is locked with gate.lock.", req="unlocked gate.lock",
                                                 result_success=lambda: completed_level(player, 3))\
                                    .lock_custom(req="password abominable; played Fix the Puzzle", 
                                                 objects=lvl3_backyard_objects,
                                                 player=player)

    lvl3_backyard_objects['shovel'] = GameObject('shovel')\
                                      .set_collectable()

    lvl3_backyard_objects['vegetable patch'] = GameObject('vegetable patch')\
                                               .change_description("There is a hole in the middle of this "
                                                                   "vegetable patch.\n"
                                                                   "Examine `vegetable patch.hole` to find out more!")

    lvl3_backyard_objects['vegetable patch.hole'] = Container('vegetable patch.hole', 
                                                              contains=["vegetable patch.hole.chest"], 
                                                              closedDescription="There seem to be something 5 inches down.",
                                                              dug=0)\
                                                    .add_command("dig", "Dig through hole.",
                                                                 successMsg="You dug 1 inch down.",
                                                                 failMsg="You need a tool...",
                                                                 req="collected shovel",
                                                                 result_success=\
                                                                 lambda: command.handle_repeated_command(
                                                                         gameObject=lvl3_backyard_objects['vegetable patch.hole'],
                                                                         counterVar="dug",
                                                                         timesNeeded=5,
                                                                         onsuccessMsg=("You hit your shovel hard on something. "
                                                                                      "Looks like a chest (vegetable patch.hole"
                                                                                      ".chest)!"),
                                                                         onsuccess=\
                                                                         lambda: lvl3_backyard_objects['vegetable patch.hole']\
                                                                                 .open(lvl3_places['backyard'])
                                                                        )
                                                                )

    lvl3_backyard_objects['vegetable patch'].add_included_item(lvl3_backyard_objects['vegetable patch.hole'])

    lvl3_backyard_objects['vegetable patch.hole.chest'] = Container('vegetable patch.hole.chest', 
                                                                    contains=['vegetable patch.hole.chest.key'])\
                                                          .add_command('open', "Opens the chest.",
                                                                       successMsg="You opened the chest.",
                                                                       result_success=\
                                                                       lambda: lvl3_backyard_objects['vegetable patch.hole.chest']\
                                                                               .open(lvl3_places['backyard']))\
                                                          .set_accessibility(False)
                                                                               
    lvl3_backyard_objects['vegetable patch.hole.chest.key'] = GameObject('vegetable patch.hole.chest.key')\
                                                              .set_collectable()\
                                                              .set_accessibility(False)

    lvl3_places['backyard'] = Place('backyard', objects=lvl3_backyard_objects) 

    lvl3_shelter_objects = {}
    lvl3_shelter_objects['drawer'] = Container('drawer', contains=['drawer.remote control'])\
                                     .add_command('open', 'Opens the drawer',
                                                  successMsg="You opened the chest. There's something inside.",
                                                  failMsg="Drawer is locked with `drawer.lock`.",
                                                  req="unlocked drawer.lock",
                                                  result_success=lambda: lvl3_shelter_objects['drawer'].open(lvl3_places['shelter']))\
                                     .lock_with_key("vegetable patch.hole.chest.key", objects=lvl3_shelter_objects, player=player)
    
    lvl3_shelter_objects['drawer.remote control'] = GameObject("drawer.remote control")\
                                                    .set_collectable()\
                                                    .set_accessibility(False)
    
    lvl3_shelter_objects['television'] = GameObject("television", on=False)\
                                         .change_description("A workable television.")\
                                         .add_command('switch', "Switch on / off the television, whichever applies",
                                                      failMsg="You need a remote control...",
                                                      req="collected drawer.remote control",
                                                      result_success=\
                                                      lambda: switch_boolean_state(
                                                              lvl3_shelter_objects['television'], 'on',
                                                              whenTrueMsg=('A drama series is on air. The protagonist said: "'
                                                                           'The password is satis..." Suddenly, the television '
                                                                           'crashed.'),
                                                              whenFalseMsg=("The television is turned off. Suddenly, the remote "
                                                                            "control glowed."),
                                                              onTrue=None,
                                                              onFalse=lambda: lvl3_shelter_objects['drawer.remote control'].\
                                                                              change_description("The back of the remote "
                                                                                                 "control shows 'abominable'.")
                                                              )
                                                     )

    lvl3_places['shelter'] = Place('shelter', objects=lvl3_shelter_objects)  
    LEVELS.append(Level(3, places=lvl3_places, startPlace="backyard"))

    lvl4_maze = Maze(['....#.###...',
                      '#.#....###.#',
                      '...###..##.#',
                      '##...#####..',
                      '.##...###..#',
                      '.##.#.....##',
                      '..#.#######.',
                      '............'], player=player)
    lvl4_endobjects = {}
    lvl4_endobjects['door'] = Door('door', opened=False, closedMsg="Door is locked with `door.lock`", 
                                   openMsg="Door is opened. You may leave now.")\
                              .add_command("open", "Opens the door.", 
                                            successMsg="You escaped the maze.\nLevel 4 must be a piece of cake, isn't it?",
                                            failMsg="Door is locked with door.lock.", req="unlocked door.lock",
                                            result_success=lambda: completed_level(player, 4))\
                              .lock_with_key('chest.key', objects=lvl4_endobjects, player=player)

    lvl4_maze[(4, 0)].add_game_objects(lvl4_endobjects)

    lvl4_chest_place_objects = {}
    lvl4_chest_place_objects['chest'] = Container('chest', contains=['chest.key'], )\
                                        .add_command('open', "Opens the chest.", 
                                                     successMsg="You opened the chest and found something glittery...",
                                                     result_success=lambda: lvl4_chest_place_objects['chest']\
                                                                            .open(lvl4_maze[(0, 11)]))                                                                    
    lvl4_chest_place_objects['chest.key'] = GameObject('chest.key')\
                                            .set_collectable()\
                                            .set_accessibility(False)

    lvl4_maze[(0, 11)].add_game_objects(lvl4_chest_place_objects)

    LEVELS.append(Level(4, places=lvl4_maze.places, startPlace=(0, 0), 
                        msgOnEnter="You are in a maze and you have to escape. "
                                   "Explore using `move left`, `move right`, `move up` or `move down`."))

    lvl5_places = {}
    lvl5_computer_lab_objects = {}
    lvl5_computer_lab_objects['computer'] = GameObject('computer')\
                                            .change_description('This computer is turned off.')\
                                            .add_command('switch', "Switch the computer on/off, whichever applies.",
                                                         successMsg="You switched on the computer. There is a game (`computer.game`) inside.",
                                                         result_success=lambda: lvl5_computer_lab_objects['computer.game'].set_accessibility(True))

    lvl5_computer_lab_objects['computer.game'] = GameObject('computer.game')\
                                                 .change_description("Play this Tic Tac Toe game!")\
                                                 .set_accessibility(False)\
                                                 .add_command('play', "Play this game.",
                                                              successMsg=("You beat the computer and was gloating. "
                                                                          "You did not realise the snickering sound of the computer.\n"
                                                                          "Suddenly, Swoosh!\n"
                                                                          "The computer sucked you in!!!"),
                                                              failMsg="Sorry, you did not beat the computer...",
                                                              req="played Tic Tac Toe",
                                                              result_success=\
                                                              lambda: (player.set_current_place(lvl5_places['room']),
                                                                       lvl5_places['room'].describe_place(),
                                                                       lvl5_places['room'].set_reachable(True),
                                                                       lvl5_places['computer lab'].set_reachable(False))
                                                              )
    
    lvl5_computer_lab_objects['door'] = Door('door', opened=False, closedMsg="Open the door, please.")\
                                        .set_accessibility(False)\
                                        .add_command('open', "Opens the door",
                                                     successMsg="You opened the door! Congratulations, you completed Level 5!",
                                                     result_success=lambda: completed_level(player, 5))

    lvl5_places['computer lab'] = Place('computer lab', objects=lvl5_computer_lab_objects)

    lvl5_room_objects = {}
    lvl5_room_objects['crafting table'] = GameObject('crafting table', charged=False)\
                                          .change_description("Craftable items: crafting table.wooden pickaxe, crafting table.stone pickaxe, "
                                                              "crafting table.iron key, crafting table.diamond key")\
                                          .set_collectable(req='collected iron chest.potion.strength orbs',
                                                           onFail="This item is too heavy for your "
                                                                  "miserable, puny hands to carry.")\
                                          .add_command('place', "Place the crafting table in this place.",
                                                       successMsg="You placed the crafting table.",
                                                       failMsg="You must collect this item first before you can place...",
                                                       req="collected crafting table",
                                                       result_success=\
                                                       lambda: (relocate_item('crafting table',
                                                                              from_=find_item_place(lvl5_places, 'crafting table'), 
                                                                              to=player.place),
                                                                player.remove_item('crafting table'),
                                                                find_item_place(lvl5_places, 'crafting table').objects['crafting table']\
                                                                .set_value('charged', find_item_place(lvl5_places, 'crafting table').name == 'workroom')
                                                               )
                                                       )

    lvl5_room_objects['iron chest'] = Container('iron chest', contains=['iron chest.potion'])\
                                      .add_command('open', "Opens the chest", 
                                                   successMsg="You opened the chest. Wait.. A potion?!",
                                                   result_success=lambda: lvl5_room_objects['iron chest']\
                                                                          .open(lvl5_places['room']))\
                                      .add_command('mine', "Why is this here?",
                                                   successMsg="You got some iron and you saw... a basement door?",
                                                   failMsg="You can only mine iron using a stone pickaxe, sir.",
                                                   req="collected crafting table.stone pickaxe",
                                                   result_success=\
                                                   lambda: (lvl5_room_objects['basement door'].set_accessibility(True),
                                                            lvl5_room_objects['iron chest.iron'].set_accessibility(True)\
                                                                                                .force_object_collection(player)))
    
    lvl5_room_objects['iron chest.iron'] = GameObject('iron chest.iron')\
                                           .change_description('Can be used to craft an iron key.')\
                                           .set_accessibility(False)
    
    lvl5_room_objects['basement door'] = Door('basement door', opened=False)\
                                         .set_accessibility(False)\
                                         .add_command('open', "Opens door",successMsg="You opened the door!",
                                                      failMsg="Door is locked with `basement door.lock`.",
                                                      req="unlocked basement door.lock",
                                                      result_success=lambda: lvl5_places['basement'].set_reachable(True))\
                                         .lock_with_password('easter', objects=lvl5_room_objects, player=player)       

    lvl5_room_objects['iron chest.potion'] = GameObject('iron chest.potion')\
                                             .change_description('Splash this position to get its orbs!')\
                                             .set_collectable()\
                                             .set_accessibility(False)\
                                             .add_command('splash', "Splashes potion.",
                                                          successMsg="Many orbs (iron chest.potion.strength orbs) fell "
                                                                     "onto the ground!",
                                                          failMsg="How can you splash it without holding it?",
                                                          req="collected iron chest.potion",
                                                          result_success=\
                                                          lambda : lvl5_room_objects['iron chest.potion.strength orbs']\
                                                                   .set_accessibility(True))
    
    lvl5_room_objects['iron chest.potion.strength orbs'] = GameObject('iron chest.potion.strength orbs')\
                                                           .change_description("Collecting this gives you power of Superman!")\
                                                           .set_collectable()\
                                                           .set_accessibility(False)

    lvl5_room_objects['garden door'] = Door('garden door', opened=False, closedMsg="Open the door, please.")\
                                       .add_command('open', "Opens the door", successMsg="Door is opened.",
                                                    result_success=lambda: lvl5_places['garden'].set_reachable(True))

    lvl5_room_objects['workroom door'] = Door('workroom door', opened=False, closedMsg="Open the door, please.")\
                                       .add_command('open', "Opens the door", successMsg="Door is opened.",
                                                    result_success=lambda: lvl5_places['workroom'].set_reachable(True))

    lvl5_room_objects['stone'] = GameObject('stone')\
                                 .change_description("Stone can craft `crafting table.stone pickaxe`.")\
                                 .add_command('mine', "Mines stone.",
                                              failMsg="You can only mine stone with a wooden pickaxe.",
                                              req="collected crafting table.wooden pickaxe",
                                              result_success=lambda: lvl5_room_objects['stone']\
                                                                     .force_object_collection(player))

    lvl5_places['room'] = Place('room', objects=lvl5_room_objects, reachable=False)

    lvl5_garden_objects = {}
    lvl5_garden_objects['tree'] = GameObject('tree')\
                                  .change_description("Punch this tree for wood.")\
                                  .add_command('punch', "Punch a tree to get wood!",
                                               failMsg="Are you sure you want to break your fingers?",
                                               req="collected iron chest.potion.strength orbs",
                                               result_success=\
                                               lambda: lvl5_garden_objects['tree.wood']\
                                                       .force_object_collection(player))

    lvl5_garden_objects['tree.wood'] = GameObject('tree.wood')\
                                       .change_description('This item can be used for crafting.')
                                        
    lvl5_places['garden'] = Place('garden', objects=lvl5_garden_objects, reachable=False)

    lvl5_workroom_objects = {}

    lvl5_workroom_objects['plug'] = GameObject('plug')\
                                    .change_description("Seems to be a plug for a crafting table...")

    lvl5_workroom_objects['crafting table.wooden pickaxe'] = \
        GameObject('crafting table.wooden pickaxe')\
        .change_description("Mines stone.")\
        .add_command('craft', "Craft a wooden pickaxe.",
                     successMsg="You crafted one with wood!",
                     failMsg="You need a charged crafting table and some wood.",
                     req=lambda: 'tree.wood' in player.inventory and find_item_place(lvl5_places, 'crafting table').name == "workroom",
                     result_success=\
                     lambda: (lvl5_workroom_objects['crafting table.wooden pickaxe'].force_object_collection(player),
                              player.remove_item('tree.wood'))
                    )

    lvl5_workroom_objects['crafting table.stone pickaxe'] = \
        GameObject('crafting table.stone pickaxe')\
        .change_description("Mines iron.")\
        .add_command('craft', "Craft a stone pickaxe.",
                     successMsg="You crafted one with stone!",
                     failMsg="You need a charged crafting table and some stone.",
                     req=lambda: 'stone' in player.inventory and find_item_place(lvl5_places, 'crafting table').name == "workroom",
                     result_success=\
                     lambda: (lvl5_workroom_objects['crafting table.stone pickaxe'].force_object_collection(player),
                              player.remove_item('stone'))
                    )

    lvl5_workroom_objects['crafting table.iron key'] = \
        GameObject('crafting table.iron key')\
        .change_description("A key to a door, with some inscriptions?")\
        .add_command('craft', "Craft an iron key.",
                     successMsg="You crafted one with iron!",
                     failMsg="You need a charged crafting table and iron.",
                     req=lambda: 'iron chest.iron' in player.inventory and find_item_place(lvl5_places, 'crafting table').name == "workroom",
                     result_success=\
                     lambda: (lvl5_workroom_objects['crafting table.iron key'].force_object_collection(player),
                              player.remove_item('iron chest.iron'))
                    )\
        .add_command('feel', "Feels the iron key.",
                     successMsg="You felt `⠞⠓⠑ ⠏⠁⠎⠎⠺⠕⠗⠙ ⠊⠎ ⠄⠑⠁⠎⠞⠑⠗⠄⠲`.",
                     failMsg="How can you feel one without crafting one?",
                     req="collected crafting table.iron key")

    lvl5_workroom_objects['crafting table.diamond key'] = \
        GameObject('crafting table.diamond key')\
        .change_description("A diamond key.")\
        .add_command('craft', "Craft a diamond key.",
                     successMsg="You crafted one with diamonds!",
                     failMsg="You need a charged crafting table and diamonds.",
                     req=lambda: 'chest.diamonds' in player.inventory and find_item_place(lvl5_places, 'crafting table').name == "workroom",
                     result_success=\
                     lambda: (lvl5_workroom_objects['crafting table.diamond key'].force_object_collection(player),
                              player.remove_item('chest.diamonds'))
                    )   

    lvl5_places['workroom'] = Place('workroom', objects=lvl5_workroom_objects, reachable=False)

    lvl5_basement_objects = {}
    lvl5_basement_objects['chest'] = Container("chest", contains=["chest.diamonds"], closedDescription="Chest is locked with `chest.lock`")\
                                     .add_command("open", "Opens the door",
                                                  successMsg="You opened the chest, and a brillant light blinded you.",
                                                  failMsg="Chest is locked with `chest.lock`",
                                                  req="unlocked chest.lock",
                                                  result_success=lambda : lvl5_basement_objects['chest']\
                                                                          .open(lvl5_places['basement']))\
                                     .lock_with_key("crafting table.iron key", objects=lvl5_basement_objects, player=player)

    lvl5_basement_objects['chest.diamonds'] = GameObject('chest.diamonds')\
                                              .set_accessibility(False)\
                                              .change_description("Can craft diamond keys.")\
                                              .set_collectable()

    lvl5_basement_objects['diamond door'] = Door('diamond door', opened=False, 
                                                 closedMsg="This door is locked with `diamond door.lock`.")\
                                            .add_command("open", "Opens the door.",
                                                         successMsg=("You opened the door and was sucked into it. Whoosh...! "
                                                                     "You are back to the computer lab, and a door magically appeared!"),
                                                         failMsg="The door is locked with `diamond door.lock`.",
                                                         req="unlocked diamond door.lock",
                                                         result_success=\
                                                         lambda: (player.set_current_place(lvl5_places['computer lab']),
                                                                 lvl5_computer_lab_objects['computer'].set_accessibility(False),
                                                                 lvl5_computer_lab_objects['computer.game'].set_accessibility(False),
                                                                 lvl5_computer_lab_objects['door'].set_accessibility(True),
                                                                 lvl5_places['computer lab'].describe_place(),
                                                                 lvl5_places['computer lab'].set_reachable(True),
                                                                 lvl5_places['room'].set_reachable(False),
                                                                 lvl5_places['garden'].set_reachable(False),
                                                                 lvl5_places['workroom'].set_reachable(False),
                                                                 lvl5_places['basement'].set_reachable(False)))\
                                            .lock_with_key('crafting table.diamond key', objects=lvl5_basement_objects, player=player)

    lvl5_places['basement'] = Place('basement', objects=lvl5_basement_objects, reachable=False)

    LEVELS.append(Level(5, places=lvl5_places, startPlace='computer lab'))

def play_level(level, player):
    """Starts `level` with `player`.
    
    Args:
        level (int): The level to start playing.
        player (player.Player): The current user playing the game.
    Returns:
        None
    """
    print()
    print("Level %d" % level)
    print("--------")
    # Initialise level and describe the player's current place into the console.
    player.reset()
    player.level = level
    levelMap = LEVELS[level - 1]
    levelMap.show_introduction()
    playerPlace = levelMap.places[levelMap.startPlace]
    player.set_current_place(playerPlace)
    playerPlace.describe_place()

    # Get commands from player until this level is completed.
    # When a level is completed, a signal will be sent to increment the player's level.
    while player.level == level:
        command.get_and_execute_user_command(player, levelMap)
