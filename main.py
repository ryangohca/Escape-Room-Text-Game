"""
A simple escape room game. Feel free to break it.
PLEASE READ requirements.txt FIRST BEFORE RUNNING THIS FILE.
Run this file to play the game.
Produced by Ryan Goh, 2I for CEP Project 1.
"""
import minigames
import levels
import utils
import player
import game_objects
# Provide screenshot

# Functions
def print_header():
    """Print the starting message."""
    print("Welcome to this escape room game!")
    print()
    print("The plot")
    print("----------")
    print("This is 3100, and many more technologies had been created,") 
    print("including strange things like game locks (locks that open if")
    print("you win in a game), x-ray glasses that can see through things")
    print("etc.")
    print()
    print("You live in this era, and being as unlucky as you would be, you")
    print("are kidnapped and locked in a suspicious room.")
    print("Of course, you have to escape FAST, or risk death by the strong")
    print("lasers that would kill you in an hour's time...")
    print()
    print("Instructions")
    print("--------------")
    game_objects.show_help_message(None)
    print()
    input("Once you are ready and read through the instructions, press enter to start the game: ")

def main():
    """Runs game. Quits gracefully when `KeyboardInterrupt` is thrown."""
    # set up
    try:
        the_player = player.Player()
        minigames.set_up_games()
        levels.make_levels(the_player)
        # start game.
        print_header()
        levels.play_level(level=1, player=the_player) # Change this number to start on a different level.
    except KeyboardInterrupt: 
        # User tries to exit the improper way.
        # Catching this will prevent an ugly exception to be printed on the console.
        print() # Add newline so that the quit message would not continue on with the other messages.
        utils.print_quit_message()

if __name__ == '__main__':
    # Runs the game if this module is run on its own (not imported).
    main()

# Of course, if you are very frustrated with the game, 'quit' and run `import cheats`.
