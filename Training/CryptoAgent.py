import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}



import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from collections import deque
import random

REPLAY_MEMORY_SIZE = 10000
DEFAULT_LOOKBACK_WINDOW = 10

import tensorflow as tf
tf.get_logger().setLevel('INFO')

# set memory growth to true



class CryptoAgent():
    def __init__(self, replay_capacity=REPLAY_MEMORY_SIZE, input_shape=(DEFAULT_LOOKBACK_WINDOW, 23)):
        self.capacity = replay_capacity
        self.memory = deque(maxlen=replay_capacity)
        self.populated = False

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
        model.add(layers.LSTM(32, activation='relu', input_shape=self.input_shape))
        model.add(layers.Dense(3))
        model.compile(optimizer='adam', loss='mse', metrics=['mae', 'accuracy'])
        return model

    def fit_network_q(self, batch_size):
        self.batch_size = batch_size

    def predict_network_q(self, state):
        self.state = state
        self.q_policy = self.model_q.predict(self.state, verbose = 0)
        return self.q_policy

    def predict_network_target(self, state):
        self.state = state
        self.q_policy = self.model_target.predict(self.state, verbose = 0)
        return self.q_policy

    def update_network_target(self):
        self.network_target.set_weights(self.model_q.get_weights())