"""Places in the game."""
class Place:
    """A place in the game. Each place has many game objects.
    
    Attributes:
        objects (dict): All the objects in the game. Must be a mapping of a string, the object's name,
                        to the game_objects.GameObject itself.
        name (str): Name of the place.
        baseObjects (list): List of names of objects that the player first see when he enters this place.
        reachable (bool): Indicates whether the player can move into this place or not.

    Methods:
        describe_place(): 
            Prints the room's description and objects to the game console.

        add_game_objects():
            Add additional object(s) into this place.

        set_reachable(flag):
            Changes the setting of whether players can enter this place.

        place_object(obj):
            An object was placed here by the player.

        delete_object(obj):
            Deletes an object in this place.
            
    """
    def __init__(self, name, objects, reachable=True):
        self.objects = {}
        self.name = name
        self.baseObjects = []
        self.reachable = reachable
        self.add_game_objects(objects)
    
    def describe_place(self):
        """Prints the room's description and objects to the game console."""
        self.get_update_on_base_objects()
        print("This is a %s." % self.name)
        if len(self.baseObjects) != 0:
            print("You saw %s." % ', '.join(self.baseObjects))
        else:
            print("You saw nothing interesting.")

    def get_update_on_base_objects(self):
        """Updates the list of base objects, lest a base object's accessibility changed."""
        self.baseObjects.clear()
        for obj in self.objects:
            if '.' in obj:
                # An object tagged to another object cannot be the base object.
                continue
            gameObj = self.objects[obj]
            if gameObj.accessible:
                self.baseObjects.append(obj)
            
    def add_game_objects(self, gameObjectDict):
        """Add additional object(s) into this place.
        
        Args:
            gameObjectDict (dict): A dictionary, mapping the game objects' names to the objects itself.
        Returns:
            self (for method chaining)
        """
        for gameObject in gameObjectDict:
            self.objects[gameObject] = gameObjectDict[gameObject]
            self.objects[gameObject].place = self
            # Iterating a dictionary only iterates the keys.
            if '.' in gameObject:
                # Object not at base level (first seen when the room is entered),
                # but with some redirection.
                continue
            elif not gameObjectDict[gameObject].accessible:
                continue
            # Set all the tagged objects accessibility to True.
            self.objects[gameObject].set_accessibility(True)
        self.get_update_on_base_objects()
        return self

    def place_object(self, obj):
        """An object was placed here by the player.

        Args:
            obj (game_objects.GameObject): The object being placed.
        Returns:
            None
        """
        self.add_game_objects({obj.name: obj})

    def delete_object(self, obj):
        """Deletes an object in this place.

        Args:
            obj (game_objects.GameObject): Object that is being deleted.
        Returns:
            None
        Raises:
            ValueError: obj not in place.
        """
        if obj.name not in self.objects:
            raise ValueError("object not in place `from_`")
        if obj.name in self.baseObjects:
            self.baseObjects.remove(obj.name)
        self.objects[obj.name].place = None
        self.objects.pop(obj.name)

    def set_reachable(self, flag):
        """Changes the setting of whether players can enter this place.
        
        Args:
            flag (bool): Determines whether this place should be available to the player or not.
        Returns:
            self (for method chaining)
        """
        self.reachable = flag
        return self

class MazeGrid(Place):
    """Represents a grid in a maze.

    Inherits from Place.
    Attributes defined here:
        x (int): The x-coordinate of this grid in the maze.
        y (int): The y-coordinate of this grid in the maze.

    Methods defined here:
        describe_place():
            Prints the room's description and objects to the game console.
            (overridden to show coordinates instead of name.)
    """
    def __init__(self, x, y, objects, reachable=True):
        super().__init__((x, y), objects=objects, reachable=reachable)
        self.x, self.y = x, y
        # Remove directional game objects' names so that their names are not printed onto the console. 
        for direction in ['left', 'right', 'up', 'down']:
            self.baseObjects.remove(direction)
        
    def describe_place(self):
        """Prints the room's description and objects to the game console."""
        print("Your coordinates in this maze is (%d, %d)." % (self.x, self.y))
        if len(self.baseObjects) != 0:
            print("You saw %s." % ', '.join(self.baseObjects))
        else:
            print("You saw nothing interesting.")
