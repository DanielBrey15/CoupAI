"""
wrapInput was a function previously used to give the user an option to quit
the program in the middle of running. This was only useful when humans were 
making moves in the game.

Since functionality to allow humans to play with AI agents will be created
in the future, I'm leaving this here for now.
"""
def wrapInput(question: str):
        # Note: Function is only used with human players
        response = input(question)
        if(response == "quit"):
            raise ValueError("Quit")
        else:
            return response