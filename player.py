"""Implements player in the game."""
import utils
import minigames
class Player:
    """The one and only player. Please do not create more than 1 copy of
       this object.
       
    Attributes:
        inventory (dict): What the player had collected. Maps a string, the object's name, to the object itself.
        opened (set): Keeps track of what containers had the player opened. This set contains strings, the container's
                      name.  
        unlocked (set): Keeps track of what locks had the player unlocked. This set contains strings, the lock's
                        name.

    Methods:
        reset(): 
            Resets the player's state. Usually called at the start of each level.

        advance_level():
            Update player that he had proceeded to the next level.

        collect_item(item, collectRequirements):
            Collects item if the collection requirement is fulfilled.

        remove_item(item):
            Removes a collected `item`.

        show_inventory():
            Prints player's inventory on console.
        
        opened_object(lockedObject):
            Update player that a locked object had been opened.

        unlocked_lock(lock):
            Update player that a lock had been unlocked.

        set_current_place(place):
            Teleports the player into the requested place, so that he can interact with the objects there.
        
        fulfill_requirement(requirement):
            Checks that player's state fulfils the requirement given.

        enter_password(password):
            Ask the player to enter a password until he quits or he enters the correct password.
    """
    def __init__(self):
        self.reset()
        self.level = 1

    def reset(self):
        """Resets the player's state."""
        self.inventory = {}
        self.opened = set()
        self.unlocked = set()
        
    def advance_level(self):
        """Update player that he had proceeded to the next level."""
        self.level += 1

    def collect_item(self, item, collectRequirements):
        """Collects `item` if `collectRequirements` is fulfilled, and prints a message to inform player
        about the results.
        
        Args:
            item (game_objects.GameObject): The item the player is trying to collect.
            collectRequirements (str): The requirement before the object can be collected.
        Returns:
            None
        """
        if item.name in self.inventory:
            print("Item had already been collected.")
        elif not item.collectable or not item.accessible or not self.fulfill_requirement(collectRequirements):
            print(item.collectionFailMsg)
        else:
            print("`%s` has been added to your inventory." % item.name)
            self.inventory[item.name] = item
    
    def remove_item(self, item):
        """Removes a collected `item`. 
        
        Args:
            item (str): The name of the game object to be removed from the player's inventory.
        Returns:
            None
        Raises:
            ValueError: The item is not found in the player's inventory.
        """
        success = True
        try:
            self.inventory.pop(item)
        except ValueError:
            # If you raise an exception here, the KeyError will be shown.
            success = False
        if not success:
            raise ValueError("Item not in player's inventory.")

    def show_inventory(self):
        """Prints player's inventory on console."""
        if len(self.inventory) != 0:
            print("You have on you: %s." % ', '.join(self.inventory))
        else:
            print("You have nothing on you.")

    def opened_object(self, lockedObject):
        """Update player that `lockedObject` had been opened.
        
        Args:
            lockedObject (str): The name of the locked object opened.
        Returns:
            None
        """
        self.opened.add(lockedObject)

    def unlocked_lock(self, lock):
        """Update player that `lock` had been unlocked.

        Args:
            lock (str): The name of the unlocked lock.
        Returns:
            None
        """
        self.unlocked.add(lock)

    def set_current_place(self, place):
        """Teleports the player into the `place`, and so can interact with the objects there.
        
        Args:
            place: (place.Place): The place the player had gone into.
        Returns:
            None
        """
        self.place = place

    def fulfill_requirement(self, requirements):
        """Checks that player's state fulfills the requirement given.
        
        Args:
            requirements (str/func): The requirement the player had to fulfil. If this is not None, this string must be
                                     a semicolon-separated of requiremnts, with each requirement having a basic requirement form,
                                     or a custom function that returns True if the requirement is fulfiled.

                                     The basic requirements forms are:
                                     "unlocked [noun]": Checks whether the lock is unlocked or not.
                                     "opened [noun]": Checks whether a container/door is unlocked or not.
                                     "collected [noun]": Checks whether the object is in the player's inventory 
                                                         or not.
                                     "password [pwd]": Checks whether the password given by the player 
                                                       is the same as the password 'pwd' given.
                                     "played [game]": Checks whether the player played the game successfully.

        Returns:
            bool: Whether the requirement is fulfiled by the player, or not.
                                  
        """
        if requirements is None:
            return True
        elif callable(requirements):
            return requirements()
        requirements = requirements.split(';')
        requirementFulfilled = True
        for requirement in requirements:
            adj, gameObject = utils.separate_first_from_last(requirement)
            if adj == 'unlocked':
                if gameObject not in self.unlocked:
                    requirementFulfilled = False
            elif adj == 'opened':
                if gameObject not in self.opened:
                    requirementFulfilled = False
            elif adj == 'collected':
                if gameObject not in self.inventory:
                    requirementFulfilled = False
            elif adj == 'password':
                # This is a special case where the condition involves input from the player. The syntax is
                #`password [password]`, and so [password] is parsed as gameObject above, not knowing this
                # special case.
                password = gameObject
                requirementFulfilled = self.enter_password(password)
            elif adj == 'played':
                requirementFulfilled = minigames.GAMES[gameObject].run()
            if not requirementFulfilled:
                return False # Short-circuit evaluation.
        return requirementFulfilled

    def enter_password(self, password):
        """This function repeatedly askes the player to enter a password until he quits or 
        had guessed the correct password.
        
        Args:
            password (str): The required password.
        Returns:
            bool: `False` if the player gives up trying to key in the password, and `True` if the 
                  player succeeds in figuring out the password.
        """
        while True:
            user_password = input("Enter a password, or `q` to stop trying: ").strip().lower()
            if user_password == 'q':
                return False
            if user_password == password:
                return True
            print("Incorrect password, try again.")
            