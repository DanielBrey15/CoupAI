# CoupAI
Developing AI agents for card game Coup

Overview of Coup: With 2 characters with unique abilities, Players use bluffing and strategy to try to be the last player standing.
Rules: https://www.qugs.org/rules/r131357.pdf (Rules also in CoupRules.pdf)

Initially created functionality to play Coup and developed various AI players with different heuristics and strategies (History folder). Currently designing and iterating on AI players that use machine learning to make their game decisions (CoupEnvironment folder).

Next steps:

There are parts of the game that I have removed while beginning training of the agent (such as making decisions based on its actual cards and calling out actions). Once I am able to teach the agent certain moves it should make (such as moves that will win it the game), I will move back to these other parts of the game.

* Store reinforcement model after training
* Use different inputs to train the model (such as which cards we have and what moves have been made)
* Include calling out probability
* Shuffle player order
* Inlcude reinforcement learning model within one player class, and have that player use makeMove (similar to the previous AIPlayer classes)

Future plans:
* Train model to determine when the agent should call out an opponent's action
* Give negative rewards for completing actions that are risky (such as those you cannot do based on your cards)
* Give negative rewards for moves where you are blocked (therefore wasting your turn)
* Allow model to decide if it wants to lie about blocking
* Try other policy-based reinforcement algorithms to make moves (such as actor-critic)
