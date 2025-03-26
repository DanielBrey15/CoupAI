def wrapInput(question: str):
        # Function is only used with human players
        response = input(question)
        if(response == "quit"):
            raise ValueError("Quit")
        else:
            return response