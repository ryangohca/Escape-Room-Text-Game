"""Game objects related functions and classes."""
import command
from place import Place

class GameObject:
    """Represents an object in the game. Each object has some commands for the player to interact with.
    
    Attributes:
        name (str): Name of this object
        collectable (bool): Determines whether the player can collect this object and put it
                           into his inventory. Default False.
        collectionReq (str): The basic requirement that must be fulfiled before collection. If defined,
                             collectionReq must be of form '[adj/noun/verb] [game object's name]' Defaults
                             None
        description (str): Description to be printed to the console whenever object is examined by the player.
                           Defaults "Nothing to examine here."
        commands (dict): Represents the available commands the object has. Dictionary must map a string, the
                         name of the command, to a command.Command object. Defaults {}
        thingsOn (list): Additional items that needs to be available if this object is available. Items in thingsOn must
                         be GameObjects. Defaults False.
        accessible (bool): Represents whether this object is accessible to the player (ie. the player can interact
                           with it). Defaults False
        collectionFailMsg (str): Message to be printed when this object cannot be collected by the player.
                                 Defaults "Sorry, item cannot be collected.".
        place (place.Place): The name of the location this object is located. Set by place.Place.
        kwargs (dict): Any other attributes that was defined to this object.

     Methods:
        add_command(commandType, commandDescription, *, successMsg=None, failMsg=None, result_success=None):
            Adds a new command to this game object. More information on this function docstring.

        run_command(player, commandType): 
            Runs the command `commandType` and update player' state.
        
        change_description(desc): 
            Changes self.description to `desc`.
        
        examine(): 
            Describes the object and print its description into the console.
        
        set_collectable(req=None, onFail=None): 
            Enables the collection of this object by player, if `req` is fulfilled or None.
            Prints onFail onto the console if `req` is not fulfilled. 
        
        disable_collection():
            Disables the collection of this object by player.
            
        lock_with_key(key, objects, player): 
            Lock object with key name `key`, and create a new object "[object name].lock".
        
        lock_with_password(password, objects, player): 
            Lock object with `password`, and create a new object "[object name].lock".
        
        lock_with_game(game, objects, player): 
            Adds a game lock to this object, and create a new object "[object name].lock".
        
        lock_custom(req, objects, player): 
            Adds a custom lock to this object.

        set_accessibility(flag):
            Sets whether this object and all the objects in self.thingsOn can be accessible by
            the player. Also recurses through the objects in self.thingsOn.

        add_included_item(item):
            Attach another item on this object.

        provide_help():
            Show the object's help screen. 

    Private methods:
        __lock(helpMsg, failMsg, req, objects, player):
            Locks object by creating a new object "[object name].lock".
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self.collectable = False
        self.collectionReq = None
        self.description = "Nothing to examine here."
        self.kwargs = kwargs
        self.commands = {}
        self.thingsOn = []
        self.accessible = True
        self.collectionFailMsg = "Sorry, item cannot be collected."
        self.place = None

    def set_value(self, attr, val):
        """Sets value val into keyword argument `attr` in constructor.

        Args:
            attr (str): Name of the atrribute to change.
            val (any): Value to change to.
        Returns:
            self (for method chaining)
        Note:
            This function is required as lambda does not support assignments.
        """
        self.kwargs[attr] = val

    # Commands
    def add_command(self, commandType, commandDescription, *,
                    successMsg=None, failMsg=None, req=None, result_success=None):
        """Adds another command to the game object, that can only be called
           if `req` is fulfilled. If successful, `successMsg` will be printed 
           and `result_success` will be called if provided. If the command fails, 
           `failMsg` will be printed if provided.
           
           Args:
               commandType (str): Name of the command.
               commandDescription (str): Description of this command to be printed on this object's
                                   help screen.
           Keyword Args:
               successMsg (str): Message to be printed when command execution is successful. Defaults None.
               failMsg (str): Message to be printed when command execution fails. Defaults None.
               req (str/func): Requirement(s) before this command can be executed. If not None, req must be of
                               the form of a basic requirement, or a custom function that returns True
                               if requirement is fulfilled. Defaults None.

                               The basic requirements forms are:
                               "unlocked [noun]": Checks whether the lock is unlocked or not.
                               "opened [noun]": Checks whether a container/door is unlocked or not.
                               "collected [noun]": Checks whether the object is in the player's inventory 
                                                   or not.
                               "password [pwd]": Checks whether the password given by the player 
                                                 is the same as the password 'pwd' given.
                               "played [game]": Checks whether the player played the game successfully.
               result_success (func): Function to be called after successful execution of command, if implemented.
                                      Defaults None.
            Returns:
               self (for method chaining)
        """
        self.commands[commandType] = command.Command(commandDescription,
                                             successMsg=successMsg,
                                             failMsg=failMsg, req=req,
                                             onsuccess=result_success)
        return self

    def run_command(self, player, commandType):
        """Runs the given command `commandType`. If successful, the state of
           `player` may change. 
           
           Args:
               player (player.Player): The current user playing the game
               commandType (str): Name of the command invoked. 
           Returns:
               None
        """
        if commandType == 'examine':
            self.examine()
        elif commandType == 'collect':
            player.collect_item(self, self.collectionReq)
        else:
            try:
                # Check that `commandType` exists.
                self.commands[commandType] 
            except KeyError:
                print("%s has no command `%s`." % (self.name, commandType))
            else:
                # If you try to run command in the try block, it will mask a
                # lot of KeyErrors that are unrelated to not finding the 
                # command.
                self.commands[commandType].run(player)

    # Description / Examination commands functions.
    def change_description(self, desc):
        """Changes self.description to `desc`.
        
        Args:
            desc (str): New description of the object.
        Returns:
            self (for method chaining)
        """
        self.description = desc
        return self

    def examine(self):
        """Describes the object and print its description into the console."""
        print(self.description)

    # Collection setting
    def set_collectable(self, req=None, onFail=None):
        """Enables the collection of this object by player, if `req` is fulfilled or None.
        
        Args:
            req (str): Requirement before objects can be collected. req must be either None
                       (default) or a string with form "[adj/verb/noun] [game object's name]".
            onFail (str): Message to be printed when item fails to be collected. Use default if None.
        Returns:
            self (for method chaining)
        """
        self.collectable = True
        self.collectionReq = req
        if onFail is not None:
            self.collectionFailMsg = onFail
        return self

    def disable_collection(self):
        """Disables the collection of this object by player.
        
        Returns:
            self (for method chaining)
        """
        self.collectable = False
        return self

    def force_object_collection(self, player):
        """Sometimes, an object is collected by the player through other methods, but the object is 
           not collectable using a `collect` command by the player. By default, if an object `collectable` 
           state is False, it would never be collectable, but this function gets around that to collect
           these "uncollectable" objects.

           An example is when a player tries to craft something. That item is not collectable, but has to
           be collected when the player successfully crafts using other items in his inventory.

           Args:
               player (player.Player): The player of the game who needs to collect "uncollectable" stuff.
           Returns:
               None
        """
        self.set_collectable()
        player.collect_item(self, None)
        self.disable_collection()
        
    # Lock settings
    def __lock(self, helpMsg, failMsg, req, objects, player):
        """Locks object by creating a new object "[object name].lock".
        
        Args:
            helpMsg (str): Description of the unlock command.
            failMsg (str): Printed to the console when unlock command fails.
            req (str): Requirements to unlock command.
            objects (dict): A dictionary of all the items, mapping its name to the object itself.
            player (player.Player): The current user of the game.
        Returns:
            None
        """
        lockName = self.name + '.lock'
        objects[lockName] = Lock(lockName, self).add_command('unlock', helpMsg, successMsg="Lock is opened!",
                                                             failMsg=failMsg, req=req,
                                                             result_success=
                                                             lambda: objects[lockName].unlock(player))
        self.add_included_item(objects[lockName])

    def lock_with_key(self, key, objects, player):
        """Lock object with key name `key`, and create a new object "[object name].lock".
        
        Args:
            key (str): The name of the key that unlocks the key lock.
            objects (dict): A dictionary of all the items, mapping its name to the object itself.
            player (player.Player): The current user of the game.        
        Returns:
            self (for method chaining)
        """
        self.__lock(helpMsg="Opens lock if its key is obtained.", failMsg="Lock needs a key to unlock.",
                    req="collected " + key, objects=objects, player=player)
        return self

    def lock_with_password(self, password, objects, player):
        """Lock object with `password`, and create a new object "[object name].lock".

        Args:
            password (str-able): The password that unlocks the password lock.
            objects (dict): A dictionary of all the items, mapping its name to the object itself.
            player (player.Player): The current user of the game.       
        Returns:
            self (for method chaining)
        """
        self.__lock(helpMsg="Opens lock if a correct password is keyed in.", failMsg=None,
                    req="password %s" % str(password), objects=objects, player=player)
        return self

    def lock_with_game(self, game, objects, player):
        """Adds a game lock to this object, and create a new object "[object name].lock".

        Args:
            game (str): The name of the game that unlocks the game lock.
            objects (dict): A dictionary of all the items, mapping its name to the object itself.
            player (player.Player): The current user of the game.       
        Returns:
            self (for method chaining)
        """
        self.__lock(helpMsg="Opens lock if you win the game.", failMsg=None, req="played %s" % game,
                    objects=objects, player=player)
        return self
    
    def lock_custom(self, req, objects, player):
        """Adds a custom lock to this object. `req` must be syntactically parsable.
        
        Args:
            req (str): Requirements to unlock this lock.
            objects (dict): A dictionary of all the items, mapping its name to the object itself.
            player (player.Player): The current user of the game.        
        Returns:
            self (for method chaining)    
        """
        self.__lock(helpMsg="Opens lock if requirements are fulfilled.", failMsg="", req=req,
                    objects=objects, player=player)
        return self

    # Accessibility settings
    def set_accessibility(self, flag):
        """Sets whether this object and all the objects in self.thingsOn can be accessible by
           the player through the value of `flag`. Also recurses through the objects in self.thingsOn.
           
        Args:
            flag (bool): The state of the accessibility flag to be changed.
        Returns:
            self (for method chaining)   
        """
        self.accessible = flag
        for obj in self.thingsOn:
            # If this object has a certain accessibility `flag`, other objects that is on this object 
            # must also be of accessibility `flag`.
            obj.set_accessibility(flag)
        return self

    # Included items settings
    def add_included_item(self, item):
        """Attach another item on this object, and set its accessibility property to that
           of this object.

        Args:
            item (GameObject): The new item to be attached on this object.
        Returns:
            self (for method chaining)  
        """
        self.thingsOn.append(item)
        item.set_accessibility(self.accessible)
        return self

    # Help commands
    def provide_help(self):
        """Show the object's help screen."""
        self.examine()
        print()
        print("Available commands:")
        if self.collectable:
            print("'collect %s': Collect %s and add it to your inventory."
                  % (self.name, self.name))
        print("'examine %s': Place %s on closer inspection." % (self.name,
                                                                self.name))
        for commandName in self.commands:
            print("'%s %s': %s" % (commandName, self.name,
                                   self.commands[commandName].describe_self()))
        print()

class Door(GameObject):
    """A door in game.
    
    Inherited from GameObject.
    Attributes defined here:
        opened (bool): Indicates whether the door is opened or closed.
        closedMsg (str): Message to be printed during examination when door is closed.
        openMsg (str): Message to be printed during examination when door is opened.

    Methods defined here:
        examine(): 
            Prints openMsg when door is opened, closedMsg otherwise.
            (overriden)

        open(): 
            Signal that this door had been opened.
    """
    def __init__(self, name, opened, closedMsg='', openMsg='', **kwargs):
        """Initialise a door with initial `opened` state. If opened, `openMsg`
           will be printed when examined, `closed` otherwise."""
        super().__init__(name, **kwargs)
        self.opened = opened
        self.closedMsg = closedMsg
        self.openMsg = openMsg

    def examine(self):
        """Prints the door's examination results into the console."""
        if self.opened:
            print(self.openMsg)
        else:
            print(self.closedMsg)

    def open(self):
        """Signal that the door had been opened."""
        self.opened = True

class Container(GameObject):
    """An object in game that holds other object(s).
    
    Inherits from GameObject
    Attributes defined here:
        isOpen (bool): Indicate whether this container is open.
        contains (list): A list of game objects in this container. All items must be GameObjects.
        closedDescription (str): Description printed on the console when examined when it is closed.
                                 Defaults "This container is not opened."

    Methods defined here:
        describe_items(): 
            Prints the container's items into the console. Does NOT check that the 
            container is opened.

        examine(): 
            Prints the container's items to the console when container is opened,
            closedDescription otherwise.
            (overriden)

        open(openedIn): 
            Signal that the container had been opened in a place `openedIn`.
    """
    def __init__(self, name, contains, isOpen=False, closedDescription=None, **kwargs):
        super().__init__(name, isOpen=isOpen, **kwargs)
        self.isOpen = isOpen
        self.contains = contains
        self.closedDescription = closedDescription if closedDescription is not None else "This container is not opened."

    def describe_items(self):
        """Prints the container's items into the console. Does NOT check that the container is opened."""
        print("%s contains %s." % (self.name, ', '.join(self.contains)))
    
    def examine(self):
        """Prints the container's examination results into the console."""
        if self.isOpen:
            self.describe_items()
        else:
            print(self.closedDescription)

    def open(self, openedIn):
        """Signal that the container had been opened in a place `openedIn`.
        
        Args:
            openedIn (place.Place): The place where this object is opened in.
        Returns:
            None
        """
        self.isOpen = True
        if not isinstance(openedIn, Place):
            raise ValueError("A Container must be opened somewhere.")
        else:
            for gameObject in self.contains:
                openedIn.objects[gameObject].set_accessibility(True)

class Lock(GameObject):
    """Represents a lock in game that restrains player from opening objects.
    
    Inherits GameObject.
    Attributes defined here:
        lockedObject (GameObject): The object that had been locked by this lock.
        opened (bool): Indicates whether this lock had been unlocked.
    
    Methods defined here:
        unlock(player): Unlocks the lock and opens the locked object.
    """
    def __init__(self, name, lockedObject, **kwargs):
        super().__init__(name, **kwargs)
        self.lockedObject = lockedObject
        self.opened = False

    def unlock(self, player):
        """Unlocks the lock and opens the locked object, and updates player that he 
        unlocked this lock.
        
        Args:
            player (player.Player): The current user of the game.
        Returns:
            None
        """
        self.opened = True
        player.unlocked_lock(self.name)
        player.opened_object(self.lockedObject.name)

def switch_boolean_state(gameObject, booleanFlag, whenTrueMsg=None, whenFalseMsg=None, onTrue=None, onFalse=None):
    """Switchs the boolean variable `booleanFlag` in `gameObject`. If the result is True, prints `whenTrueMsg`
    and call `onTrue` if function is defined; or else, prints `whenFalseMsg` and call `onFalse` if defined.
    
    Args:
        gameObject (GameObject): The game object that would have one of its boolean attributes switched.
        booleanFlag (str): The name of the boolean attribute.
        whenTrueMsg (str): The message printed on the console when booleanFlag is True. Defaults None.
                           (nothing is printed)
        whenFalseMsg (str): The message printed on the console when booleanFlag is False. Defaults None.
                            (nothing is printed)
        onTrue (func): The function called when booleanFlag is True. Defaults None (no function is called.)
        onFalse (func): The function called when booleanFlag is False. Defaults None (no function is called.)
    Returns:
        None
    """
    gameObject.set_value(booleanFlag, not gameObject.kwargs[booleanFlag])
    if gameObject.kwargs[booleanFlag]:
        if whenTrueMsg is not None:
            print(whenTrueMsg)
        if onTrue is not None:
            onTrue()
    else:
        if whenFalseMsg is not None:
            print(whenFalseMsg)
        if onFalse is not None:
            onFalse()

def get_object(name, player, place):
    """Gets object with name `name` from either the player's inventory or the player's place. 
    If the object cannot be found, returns None.
    
    Args:
        name (str): The object's exact name.
        player (player.Player): The current user who played this game. This is needed to check his inventory
                                for the item.
        place (place.Place): The current place of the player.
    Returns:
        GameObject:
            The requested item.
        None:
            The item does not exist.
    """
    calledObject = None
    if name in place.objects:
        calledObject = place.objects[name]
    elif name in player.inventory:
        calledObject = player.inventory[name]
    if calledObject is None:
        # Object does not exist.
        return None
    elif not calledObject.accessible:
        # Object exists, but player should not see it yet.
        return None
    else:
        return calledObject

def show_help_message(gameObject):
    """Shows `gameObject` help message. If `gameObject` is None, shows the general help message instead.
    
    Args:
        No arguments: General help is requested.
        gameObject (GameObject): The object that the player needs help with.
    Returns:
        None
    """
    if gameObject is not None:
        gameObject.provide_help()
    else:
        print("""\
During the game, type `help` to show this help message, `help
[object's name]` to show the object's individual help message and
commands, `show inventory` to check your inventory`, `enter 
[place's name]` to enter a place in the game, `help places` to show
the current level's places and describes your current place
and `quit` to quit the game.""")
        print()
        print("""\
Whenever you enter a place, the game will always provide you with 
these information:
\"""
This is a [name of place].
You saw [list of interactable items].
\"""
You may ask for help on how to further interact with these items
by typing `help` + a space + [name of item in list]. Note that 
other objects may also be interactable but not shown in the list
of available items, but their names can definitely be found somewhere
in the game (eg. by examining an object).""")

def relocate_item(objName, from_, to):
    """Relocates an object from place `from_` to `to`.

    Args:
        objName (str): Name of object relocated.
        from_ (place.Place): Place of the object once located.
        to (place.Place): Place of the object where it should be placed.
    Returns:
        None
    Raises:
        ValueError: 1. object not in place `from_`
                    2. Trying to place an object in `to` with the same name as another object in `to`.
    """
    if objName in to.objects and from_ != to:
        raise ValueError("Trying to place an object in `to` with the same name as another object in `to`.")
    obj = from_.objects[objName]
    from_.delete_object(obj)
    to.place_object(obj)

def find_item_place(places, item):
    """Finds an item's place in the places given.

    Args:
        places (dict): Mapping of names of places to the places itself.
        item (str): Name of the item.
    Returns:
        place.Place: Place of the object
        None: Item not found in any of the places.
    """
    for place in places:
        if item in places[place].objects:
            return places[place]
    return None