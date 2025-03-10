from AIGame import AIGame

with open("AIGameBatchRunner.py") as my_file:
    for i in range(100):
        game = AIGame()
        game.PlayGame()