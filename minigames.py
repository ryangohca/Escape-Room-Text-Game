"""In-game minigames related classes and functions."""
import random
import sys
# Mini Games
# Each game must inherit from BasicGame and implement the `run` method, which returns True
# only if the player successfully finishes the game, False otherwise; and the `name` function
# property which returns a string: the name of the game.

# When the main game is inititalised, all the subclasses of BasicGame will also be inititalised
# in GAMES[self.name].
GAMES = {}
class BasicGame:
    """Interface for Game objects.
    
    Abstract properties:
        name(): 
            Returns the name of the game.
    Abstract methods:  
        run():
            Runs the game. Should only return True when the game is successfully completed, False
            otherwise.
    """
    def __init__(self):
        pass
    
    @property
    def name(self):
        raise NotImplementedError("Property `name` must be implemented.")

    def run(self):
        raise NotImplementedError("Method `run` must be implemented")

class Hangman(BasicGame):
    """A hangman game."""
    def __init__(self):
        super().__init__()
        self.words = {}
        self.add_words()

    @property
    def name(self):
        return "Hangman"

    def add_words(self):
        """Populate the words dictionary."""
        try:
            f = open("dictionary.txt", mode="r")
        except FileNotFoundError:
            print("`dictionary.txt` is not found in the current directory of this file.")
            print("Please ensure that `dictionary.txt` is set up properly, and rerun the game.")
            sys.exit()
        while (word := f.readline()) != '':
            # Python's hash table lookup is much faster than a list lookup.
            self.words[word.strip().lower()] = None
        f.close()

    def run(self):
        """Runs the hangman game."""
        # Since this is a simple game, I would not bother splitting it into
        # smaller functions.
        print("Starting game %s." % self.name)
        while True:
            # Initialise game.
            lives = 9
            # WARNING: I have absolutely no idea what the word will be.
            chosenWord = random.sample(self.words.keys(), 1)[0]
            guessedWord = ['_'] * len(chosenWord)
            guessedLetters = set()
            # Main game loop
            while lives > 0:
                print("You have %d lives left." % lives)
                print(*guessedWord, sep=' ')

                # Get a valid input from user.
                while True:
                    letter = input("Please enter a letter (or `quit` to quit): ").strip().lower()
                    if letter == "quit":
                        print("Game is quitting...")
                        return False
                    if len(letter) > 1:
                        print("Sorry, too many characters found. Please try again.")
                        continue
                    elif not letter.isalpha():
                        print("Sorry, the letter must be an alphabet. Please try again.")
                        continue
                    letter = letter.lower()
                    if letter in guessedLetters:
                        print("You have already guessed letter '%s'. Please try again." % letter)
                        continue
                    break

                # Updates game state.
                result = chosenWord.find(letter)
                if result == -1:
                    print("Sorry, letter '%s' is not in the required word. You lost a live." % letter)
                    lives -= 1
                else:
                    # Find all the matches
                    print("You found a correct letter '%s'!" % letter)
                    while result != -1:
                        guessedWord[result] = letter
                        result = chosenWord.find(letter,result + 1)
                guessedLetters.add(letter)

                # If there are no blanks, all letters had been guessed correctly.
                if '_' not in guessedWord:
                    print("You won! The answer is %s." % chosenWord)
                    return True

            print("Sorry, you lost. The answer is %s." % chosenWord)
            if not input("Play again? (yes / no): ").lower().strip().startswith('y'):
                return False
        return True

class Puzzle(BasicGame):
    """A puzzle game, where the player have to fix back a 8 by 7 board with only the 
    tiles given to him, without rotating any of the tiles."""
    def __init__(self):
        super().__init__()
        self.blocks = [
            ["aa",
             "a-"],
            ["bb"],
            ["ccc",
             "-c-"],
            ["-ddd",
             "dd--"],
            ["ee",
             "-e",
             "-e"],
            ["fff",
             "f--",
             "f--"],
            ["ggggg"],
            ["hh"],
            ["ii",
             "-i"],
            ["jj"],
            ["kk-",
             "kkk"],
            ["lll",
             "ll-"],
            ["mmm",
             "-m-"],
            ["---n",
             "nnnn"],
            ["oo"],
        ]

    @property
    def name(self):
        return "Fix the Puzzle"

    def maximum_height_of_blocks(self):
        """Finds the maximum amount of vertical space a block can take."""
        maxHeight = 0
        for block in self.blocks:
            maxHeight = max(maxHeight, len(block))
        return maxHeight

    def print_blocks(self):
        """Prints the blocks horizontally."""
        maxHeight = self.maximum_height_of_blocks()
        toPrint = [[] for i in range(maxHeight)] # toPrint[height] stores what should be printed at that height.
        for height in range(maxHeight):
            for block in self.blocks:
                toPrint[height].append('|')
                if height >= len(block):
                    # There is no tiles here for this block, fill it with empty spaces.
                    toPrint[height].extend([' ' for i in block[0]])
                else:
                    toPrint[height].extend([tile if tile != '-' else ' ' for tile in block[height]])
        for tiles in toPrint:
            # The first element of tiles will always be an empty space, so ignore it.
            print(*tiles[1:], sep='')

    def board_is_correct(self, board):
        """Checks whether the board is fixed currently.

        Args:
            board (list): List of strings, comprising lowercase letters, representing the
                          board the player had fixed.
        Returns:
            bool: Whether the player had actually placed all the provided blocks
                  into the board or not.
        """
        return all([in_matrix(board, block) for block in self.blocks])

    def run(self):
        """Runs this puzzle game, and returns True if the player successfully completed the puzzle."""
        print("Solve this puzzle.")
        print("You have an empty 8 by 7 board. You are given these blocks of tiles:")
        self.print_blocks()
        print("Find a way to place these blocks of tiles back into the board, with no gaps!")
        print("To make things easier (or harder), you cannot change the orientation of the blocks.")
        while True:
            print("Enter a 8 by 7 board, or `q` on any of the lines to exit:")
            print("The board must be made entirely of letters, with each block shaped like the tiles shown to you.")
            user_board = []
            # Get the user's board after the tiles were filled in
            for row in range(7):
                line = input().strip().lower()
                if line == 'q':
                    print("You quitted the game.")
                    return False
                user_board.append(line)
            for row in user_board:
                if len(row) != 8:
                    print("Your board has an incorrect size. Please try again.")
                    break # Short-circuit evaluation, if 1 is incorrect, the board is incorrect.
            else:
                # Loop did not reach `break`; input is valid
                if self.board_is_correct(user_board):
                    print("You cracked the puzzle! Good job.")
                    return True
                else:
                    print("Sorry, you did not complete the puzzle. Please try again.")

class TicTacToe(BasicGame):
    """A 4 by 4 Tic Tac Toe Game."""
    def __init__(self):
        super().__init__()

        # The arrangement that needs to be seen on the board to be considered a win.
        self.playerWinningLines = [['pppp'],
                                   ['p',
                                    'p',
                                    'p',
                                    'p'],
                                   ['p---',
                                    '-p--',
                                    '--p-',
                                    '---p'],
                                   ['---p',
                                    '--p-',
                                    '-p--',
                                    'p---']]
        
        self.computerWinningLines = [['cccc'],
                                     ['c',
                                      'c',
                                      'c',
                                      'c'],
                                     ['c---',
                                      '-c--',
                                      '--c-',
                                      '---c'],
                                     ['---c',
                                      '--c-',
                                      '-c--',
                                      'c---']]

        # Danger, someone is going to win!
        # Notice the slight exclusion of some cases. eg. 'p-pp'.
        # This ensures that the game is a little bit easier.
        self.playerGoingToWinLines = [['ppp'],
                                      ['p',
                                       'p',
                                       'p'],
                                      ['p--',
                                       '-p-',
                                       '--p'],
                                      ['--p',
                                       '-p-',
                                       'p--']]
        
        self.computerGoingToWinLines = [['ccc'],
                                        ['c',
                                         'c',
                                         'c'],
                                        ['c--',
                                         '-c-',
                                         '--c'],
                                        ['--c',
                                         '-c-',
                                         'c--']]
    @property
    def name(self):
        return "Tic Tac Toe"

    def set_up_game(self):
        """Sets up the game by resetting the state of the game."""
        self.board = []
        for i in range(5):
            self.board.append([' '] * 5)
        self.gridAvailable = set(range(1, 26))

    def show_instructions(self):
        print("""This is a unique Tic Tac Toe game. Instead of playing in 3 by 3 board,
you will be playing in a 5 by 5 board instead, and get 4 in a line to win!

The board would be as follows:
----------------
| 1| 2| 3| 4| 5|
----------------
| 6| 7| 8| 9|10|
----------------
|11|12|13|14|15|
----------------
|16|17|18|19|20|
----------------
|21|22|23|24|25|
----------------

Type that particular number on that grid to place your move there.
Type `help` to show this help message again, and `quit` to quit the game.

In the board, 'p' represets you and 'c' represents the computer.

And finally, good luck!
""")

    def print_board(self):
        """Prints the board state now."""
        print("The board now: ")
        for i in range(0, 25, 5):
            print('-' * 11) # Print separating line
            for j in range(i, i + 5, 1):
                print('|', self.board[j//5][j%5], sep='', end='') # Prints grid
            print('|')
        print('-' * 11) # Print final border horizontal line

    def get_move(self, who):
        """Gets the move for `who`.

        Args:
            who (str): Either 'computer' or 'player'. Determines who will be
                       making a move.
        Returns:
            None
        """
        if who == 'player':
            while True:
                player_move = input("Enter your move: ")
                if player_move == 'help':
                    self.show_instructions()
                    continue
                elif player_move == 'quit':
                    return 'quit'
                try:
                    player_move = int(player_move)
                except ValueError:
                    print("You did not enter an integer. Please try again.")
                    continue
                if not 0 < player_move <= 25:
                    print("Your move is out of range. Please enter an integer between 1 and 25 inclusive.")
                    continue
                if player_move not in self.gridAvailable:
                    print("That gird is already taken. Plese try again.")
                    continue
                return player_move
        elif who == 'computer':
            winningMoves = []
            necessaryBlockingMoves = []
            advantageousMoves = []
            for move in self.gridAvailable:
                # Check whether you can win or player is going to win, and try to win / block player
                # Try to play here.
                self.board[(move - 1) // 5][(move - 1) % 5] = 'c'
                if self.get_result() == "computer won": # You can win by making this move.
                    winningMoves.append(move)
                    
                # Anticipate player's next move.
                self.board[(move - 1) // 5][(move - 1) % 5] = 'p'
                if self.get_result() == "player won": # You will lose if you do not make this move.
                    necessaryBlockingMoves.append(move)

                # Check which moves are more advantageous to you
                self.board[(move - 1) // 5][(move - 1) % 5] = 'c'
                if any([in_matrix(self.board, goal) for goal in self.computerGoingToWinLines]):
                    advantageousMoves.append(move)

                # Check which moves would give the player an advantage, if player chose them the next move.
                self.board[(move - 1) // 5][(move - 1) % 5] = 'p'
                if any([in_matrix(self.board, goal) for goal in self.playerGoingToWinLines]):
                    advantageousMoves.append(move)

                # Reset `move`
                self.board[(move - 1) // 5][(move - 1) % 5] = ' '

            if len(winningMoves) != 0:
                # If you can win, why not?
                return random.choice(winningMoves)
            elif len(necessaryBlockingMoves) != 0:
                # If player can win, stop him.
                return random.choice(necessaryBlockingMoves)
            
            if len(advantageousMoves) == 0 or random.randint(1, 100) > 95:
                # There is also a 5% chance that the computer may choose a random move
                # instead of the ones advantaging it.
                return random.sample(self.gridAvailable, 1)[0]
            else:
                # Pick one of the moves that will advantage the computer
                return random.choice(advantageousMoves)

    def execute_move(self, move, who):
        """Excecutes the move by updating the board.

        Args:
            move (int): A number between 1 to 25. Determines which space is going to be occupied.
            who (str): Either 'player' or 'computer'. Determines who gets that space.
        Returns:
            None
        """
        self.board[(move - 1) // 5][(move - 1) % 5] = 'p' if who == 'player' else 'c'
        self.gridAvailable.remove(move)

    def get_result(self):
        """Gets the board's state.

        Returns:
            "player won": Player had a match of 4 and won.
            "computer won": Computer had a match of 4 and won.
            "tie": No moves left, no one wins.
            "no one won": The game is not a tie, ie. moves can still be played, and
                          no one had won yet.
        """
        if any([in_matrix(self.board, goal) for goal in self.playerWinningLines]):
            return "player won"
        elif any([in_matrix(self.board, goal) for goal in self.computerWinningLines]):
            return "computer won"
        elif len(self.gridAvailable) == 0:
            return "tie"
        else:
            return "no one won"
        
    def run(self):
        """Runs the game of 5 by 5 Tic Tac Toe."""
        self.show_instructions()
        while True:
            self.set_up_game()
            self.print_board()
            while True:
                # Your turn.
                print("Your move: ")
                player_move = self.get_move('player')
                if player_move == 'quit':
                    print("You quitted the game. Good luck next time!")
                    return False
                else:
                    self.execute_move(player_move, 'player')
                self.print_board()
                result = self.get_result()
                if result == 'player won':
                    print("Congratulations! You beat the computer!")
                    return True
                elif result == 'tie':
                    print("Sorry, it's a tie.")
                    break
                # Computer's turn
                print("It's now the computer's turn.")
                com_move = self.get_move('computer')
                self.execute_move(com_move, 'computer')
                self.print_board()
                result = self.get_result()
                if result == 'computer won':
                    print("Sorry, you did not beat the computer...")
                    break
                elif result == 'tie':
                    print("Sorry, it's a tie.")
                    break
                
            if not input("Play again? (yes / no): ").lower().strip().startswith('y'):
                return False

def count_occurances_in_matrix(bigger, smaller):
    """Counts the number of times the smaller matrix is in the bigger matrix. '-' in
    the smaller matrix represents that it could represent anything. Does not check
    whether both matrixes are valid matrixes.
    
    Time complexity: O(N^4) as we are not expecting `bigger` to be more than 50x50.

    Args:
        bigger (2d list): The bigget matrix to search in.
        smaller (2d list): The smaller matrix to find in the larger one.
    Returns:
        int: Number of times `smaller` is found inside `larger`.
    """
    if len(bigger) < len(smaller):
        # The smaller matrix height is greater than the bigger matrix height.
        return 0
    elif len(bigger[0]) < len(smaller[0]):
        # The smaller matrix length is greater than the bigger matrix length.
        return 0
    # Check every possible starting position of the smaller matrix (i1, j1)
    # in the bigger matrix.
    numOccurance = 0
    for i1 in range(len(bigger) - len(smaller) + 1):
        for j1 in range(len(bigger[i1]) - len(smaller[0]) + 1):
            idxi = 0
            found = True
            for i2 in range(i1, i1 + len(smaller)):
                idxj = 0
                for j2 in range(j1, j1 + len(smaller[0])):
                    if smaller[idxi][idxj] == '-':
                        idxj += 1
                        continue
                    if bigger[i2][j2] != smaller[idxi][idxj]:
                        found = False
                    idxj += 1
                idxi+=1
            if found:
                numOccurance += 1
    return numOccurance

def in_matrix(bigger, smaller):
    """Detemines whether the smaller matrix is in the bigger matrix. '-' in
    the smaller matrix represents that it could represent anything. Does not check
    whether both matrixes are valid matrixes.

    Args:
        bigger (2d list): The bigget matrix to search in.
        smaller (2d list): The smaller matrix to find in the larger one.
    Returns:
        bool: Determines whether `smaller` is found inside `larger`.
    """
    return count_occurances_in_matrix(bigger, smaller) >= 1
    
def set_up_games():
    """Put all the games in the `GAMES` dictionary, where the key is equal to the game class name."""
    global GAMES
    for cls in BasicGame.__subclasses__():
        game = cls()
        GAMES[game.name] = game

if __name__ == '__main__':
    set_up_games()
    GAMES['Tic Tac Toe'].run()
