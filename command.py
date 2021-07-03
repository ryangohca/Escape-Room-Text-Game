"""Command related classes and functions."""
import game_objects
import sys
import utils
class Command:
    """Describes an executable command in game.
    
    Attributes:
       successMsg (str): Messages that will be printed when command executes successfully. If
                        successMsg is None, does not print anything.
       failMsg (str): Message that will be printed if command fails. If failMsg is None, does
                     not print anything.
       req (str/func): Basic requirement(s) that must be fulfilled before command can be successful.
                       If req is None, no requirement is needed to successfully run this command. req
                       must have a basic requirement form, or a function that returns True if req is fulfilled.

                       The basic requirements forms are:
                       "unlocked [noun]": Checks whether the lock is unlocked or not.
                       "opened [noun]": Checks whether a container/door is unlocked or not.
                       "collected [noun]": Checks whether the object is in the player's inventory 
                                           or not.
                       "password [pwd]": Checks whether the password given by the player 
                                         is the same as the password 'pwd' given.
                       "played [game]": Checks whether the player played the game successfully.
       onsuccess (func): Function that will be called if command is successful. Function must have
                        no parameters. If onsuccess is None, no function is called.
       description (str): Description of this command in the help screen.

    Methods:
       run(player): 
           Runs the command and update player status if needed.
           
       describe_self(): 
           Returns the description of this command.
    """
    def __init__(self, commandDescription, successMsg, failMsg, req, onsuccess):
        """Initialise command."""
        self.successMsg = successMsg
        self.failMsg = failMsg
        self.req = req
        self.onsuccess = onsuccess
        self.description = commandDescription

    def run(self, player):
        """Runs the command and update player status if needed.

        Args: 
            player (player.Player): The current user who is playing the game.
        Returns:
            None
        """
        if player.fulfill_requirement(self.req):
            if self.successMsg is not None:
                print(self.successMsg)
            if self.onsuccess != None:
                self.onsuccess()
        else:
            if self.failMsg is not None:
                print(self.failMsg)
    
    def describe_self(self):
        """Returns a string, the description of this command."""
        return self.description

def handle_repeated_command(gameObject, counterVar, timesNeeded, onsuccessMsg, onsuccess=None):
    """Check whether `counterVar` in `gameObject` will reach `timesNeeded` after this execution of command.
       If True, `onsuccessMsg` is printed and `onsuccess` is called if implemented.
    
    Args:
        gameObject (game_objects.GameObject): The target object of this command.
        counterVar (str): A key in gameObjects.kwargs that maps to an integer.
        timesNeeded (int): Number of times this command should be repeated.
        onsuccessMsg (str): Message to be printed when this command is repeated enough times.
        onsuccess (func): A function that is called after `onsuccessMsg` is printed, if defined.
                         Default None.
    Returns:
        None
    """
    if gameObject.kwargs[counterVar] + 1 == timesNeeded: # Player succeeds on this try.
        print(onsuccessMsg)
        if onsuccess is not None:
            onsuccess()
    else:
        gameObject.kwargs[counterVar] += 1

def get_and_execute_user_command(player, levelMap):
    """Get and execute command by user.
    
    Args:
        player (player.Player): The current user playing the game.
        levelMap (levels.Level): The current level's places.
    Returns:
        None
    """
    playerPlace = player.place 
    instruction = input("Enter a command: ").lower().strip()

    if game_objects.get_object(instruction, player, playerPlace) is not None:
        # Player may had typed the name of the object alone.
        print("Type `help %s` for more information about this object." % instruction)
        return

    # Check for invalid syntax
    try:
        verb, noun = utils.separate_first_from_last(instruction)
    except ValueError:
        # Single word inputs
        if instruction == 'help':
            # General help message
            game_objects.show_help_message(None)
        elif instruction == 'quit':
            # Player quits the game.
            utils.print_quit_message()
            sys.exit() # Quits the game
        else:
            print("`%s` is not a valid command." % instruction)
        return
    # Player wants to enter a place.
    if verb == 'enter':
        try:
            playerRequestedPlace = levelMap.places[noun]
        except KeyError:
            print("`%s` is not a place." % noun)
            return
        if not playerRequestedPlace.reachable:
            print('You cannot go into `%s` yet.' % noun)
            return
        playerPlace = playerRequestedPlace
        player.set_current_place(playerPlace)
        playerPlace.describe_place()
        return

    # Showing inventory
    if verb == 'show' and noun == 'inventory':
        player.show_inventory()
        return
    
    # Help for place
    if verb == 'help' and noun == 'places':
        levelMap.show_introduction()
        playerPlace.describe_place()
        return
        
    # Check for invalid object
    calledObject = game_objects.get_object(noun, player, playerPlace)
    if calledObject is None:
        print("`%s` is not found." % noun)
        return

    # Help with object
    if verb == 'help':
        game_objects.show_help_message(calledObject)
        return

    # Other valid commands - leave to object
    calledObject.run_command(player, verb)
