import pandas as pd
import seaborn as sb
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten

import numpy as np
X = np.load('input_data.npy')
y = np.load('output_data.npy')

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

def divide_data(data, train_rate, val_rate, test_rate):
    train = data[0 : int(len(data) * train_rate)]
    val = data[int(len(data) * train_rate) : int(len(data) * (train_rate + val_rate))]
    test = data[int(len(data) * (train_rate + val_rate)) : len(data)]
    return train, val, test

X = np.expand_dims(X, axis = 2)
train_X, val_X, test_X = divide_data(X, 0.6, 0.2, 0.2)
train_y, val_y, test_y = divide_data(y, 0.6, 0.2, 0.2)
print(train_X.shape)
print(train_y.shape)

model = Sequential()
model.add(LSTM(units=100, return_sequences=True, input_shape=(train_X.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(Flatten())
model.add(Dense(units=2))
model.compile(optimizer='adam', loss='MeanSquaredError', metrics=\
              ['mean_absolute_error'])
history = model.fit(train_X, train_y, epochs=100, batch_size=64, validation_data=(val_X, val_y))

mae = history.history['mean_absolute_error']
val_mae = history.history['val_mean_absolute_error']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(mae) + 1)
plt.ylim([0, 10])
plt.plot(epochs, mae, 'bo', label='Training mae')
plt.plot(epochs, val_mae, 'b', label='Validation mae')
plt.title('Training and validation MAE')
plt.legend()
plt.figure()
plt.ylim([0, 10])
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()