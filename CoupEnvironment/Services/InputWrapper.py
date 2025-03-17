def wrapInput(question: str):
        response = input(question)
        if(response == "quit"):
            raise ValueError("Quit")
        else:
            return response