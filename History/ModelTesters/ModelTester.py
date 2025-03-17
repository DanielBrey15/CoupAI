import numpy as np
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("../CSVs/StealData.csv")

x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, shuffle=True)

model = tf.keras.models.load_model("../ModelScripts/stealModel1.keras")

predictions = model.predict(x_test)

loss, accuracy = model.evaluate(x_test, y_test)

print("loss: " + loss + " accuracy: " + accuracy)