"""Random stuff that other functions from other modules use but does not belong to any of the modules.

Functions:
    print_quit_message():
        Prints the quit message of the game.
    
    separate_first_from_last(s):
        Separates the very first word from the rest of the string, and condenses all whitespace in
        string to only 1 whitespace.
"""
def print_quit_message():
    # This function is here so that I can customise the quit message easily.
    print("You quit the game. Thank you and goodbye.")

def separate_first_from_last(s):
    """Separates the very first word from the rest of the string, and condenses all whitespace in
       string to only 1 whitespace.
       
    Args:
        s (str): The string to be streamed.
    Returns:
        tuple: the first word in `s` is in tuple[0], the rest of `s` in tuple[1]. 
    Raises:
        ValueError: `s` is a single word.
    """
    inputWords = s.split()
    if len(inputWords) <= 1:
        raise ValueError('No last.')
    first = inputWords[0]
    last = ' '.join(inputWords[1:])
    return first, last