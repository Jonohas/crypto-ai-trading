import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import gc


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from collections import deque
import random
import datetime

REPLAY_MEMORY_SIZE = 10000
DEFAULT_LOOKBACK_WINDOW = 10

import tensorflow as tf
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))

# set memory growth to true
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

class CryptoAgent():
    def __init__(self, replay_capacity=REPLAY_MEMORY_SIZE, input_shape=(DEFAULT_LOOKBACK_WINDOW, 23)):
        self.capacity = replay_capacity
        self.memory = deque(maxlen=replay_capacity)
        self.populated = False

        log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

        self.input_shape = input_shape

        self.model_q = self.build_model()

        self.model_target = self.build_model()
        self.model_target.set_weights(self.model_q.get_weights())

    def sample_from_replay_memory(self, batch_size):
        self.batch_size = batch_size
        if self.batch_size > len(self.memory):
            self.populated = False
            return self.populated
        else:
            return random.sample(self.memory, self.batch_size)

    def append_to_replay_memory(self, step):
        # Append an experience to the replay memory
        self.step = step
        self.memory.append(self.step)

    def build_model(self):
        model = keras.Sequential()

        optimizer = Adam(learning_rate=0.002)

        model.add(layers.LSTM(200, input_shape=self.input_shape, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(128, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(64, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(32))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(16, activation='relu'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(3, activation='softmax'))

        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['mae', 'accuracy'])
        return model

    def fit_network_q(self, X, y, batch_size):
        self.model_q.fit(X, y, batch_size=batch_size, verbose=0, callbacks=[self.tensorboard_callback])

    def predict_network_q(self, state):
        self.state = state
        value = tf.convert_to_tensor(self.state)
        self.q_policy = self.model_q.predict(value, verbose = 0)
        gc.collect()
        keras.backend.clear_session() 
        return self.q_policy

    def predict_network_target(self, state):
        self.state = state
        value = tf.convert_to_tensor(self.state)
        self.q_policy = self.model_target.predict(value, verbose = 0)
        gc.collect()
        keras.backend.clear_session() 
        return self.q_policy

    def update_network_target(self):
        self.network_target.set_weights(self.model_q.get_weights())