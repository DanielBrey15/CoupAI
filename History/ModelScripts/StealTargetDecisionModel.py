import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("../CSVs/StealData.csv")

x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, shuffle=True)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(21,)),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, epochs=10, batch_size=32)

model.save("stealModel1.keras")