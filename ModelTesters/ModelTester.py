import numpy as np
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("../CSVs/StealData.csv")

# Generate or load your dataset
x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, shuffle=True)

model = tf.keras.models.load_model("../ModelScripts/stealModel1.keras")

predictions = model.predict(x_test)

loss, accuracy = model.evaluate(x_test, y_test)

print("loss: " + loss + " accuracy: " + accuracy)


# print("Case 1: They've only done tax")
# predict1 = model.predict(pd.DataFrame([[
#                     totalMoveCountDict[Move.INCOME], #Total Income moves
#                     totalMoveCountDict[Move.FOREIGNAID], #Total Foreign Aid moves
#                     totalMoveCountDict[Move.COUP], #Total Coup moves
#                     totalMoveCountDict[Move.TAX], #Total Tax moves
#                     totalMoveCountDict[Move.STEAL], #Total Steal moves
#                     totalMoveCountDict[Move.ASSASSINATE], #Total Assassinate moves
#                     totalMoveCountDict[Move.EXCHANGE], #Total Exchange moves
#                     numTotalBlockStealActions, #Total Block Steal actions
#                     totalCardsLeft, #Total cards left
#                     playerMoveCountDict[Move.INCOME], #Target player's Income moves
#                     playerMoveCountDict[Move.FOREIGNAID], #Target player's Foreign Aid moves
#                     playerMoveCountDict[Move.COUP], #Target player's Coup moves
#                     playerMoveCountDict[Move.TAX], #Target player's Tax moves
#                     playerMoveCountDict[Move.STEAL], #Target player's Steal moves
#                     playerMoveCountDict[Move.ASSASSINATE], #Target player's Assassinate moves
#                     playerMoveCountDict[Move.EXCHANGE], #Target player's Exchange moves
#                     numPlayerBlockStealActions, #Target player's Block Steal actions
#                     playerNumCardsLeft, #Target player's cards left
#                     playerNumCoins, #Target player's coins
#                     myCards, #My cards
#                     myCoins #My coins
#                 ]]))