
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from collections import deque
import random

from enum import Enum

import numpy as np

from gym import spaces
import gym

# Use multiple candles as input

REPLAY_MEMORY_SIZE = 10000
BATCH_SIZE = 64
DEFAULT_LOOKBACK_WINDOW = 10

INITIAL_ACCOUNT_BALANCE = 100


class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2


class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, data, lookback_window=DEFAULT_LOOKBACK_WINDOW):
        super(CryptoEnvironment, self).__init__()
        self.data = data
        #get first value of data
        self.current_step = 0
        self.state = self.data.iloc[self.current_step]

        self._done = False

    def reset(self):
        return self.state

    def step(self, action):

        if self.current_step == len(self.data):
            self.current_step = 0
            self._done = True

        self.state = self.data.iloc[self.current_step]
        self.next_state = self.data.iloc[self.current_step + 1]

        self.current_step += 1
        return self.next_state, 0, self._done, {}

    def render(self):
        pass


class CryptoAgent():
    def __init__(self, replay_capacity=REPLAY_MEMORY_SIZE, input_shape=(DEFAULT_LOOKBACK_WINDOW, 18)):
        self.capacity = replay_capacity
        self.memory = deque(maxlen=replay_capacity)
        self.populated = False

        self.input_shape = input_shape

        self.model_q = self.build_model()

        self.model_target = self.build_model()
        self.model_target.set_weights(self.model_q.get_weights())

    def sample_from_replay_memory(self, batch_size):
        self.batch_size = batch_size
        if self.batch_size > len(self.replay_memory):
            self.populated = False
            return self.populated
        else:
            return random.sample(self.replay_memory, self.batch_size)

    def append_to_replay_memory(self, step):
        # Append an experience to the replay memory
        self.step = step
        self.replay_memory.append(self.step)

    def build_model(self):
        model = keras.Sequential()
        model.add(layers.Dense(32, input_shape=self.input_shape, activation='relu'))
        model.add(layers.Dropout(0.1))
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.Dense(3, activation='linear'))

        model.compile(optimizer='adam', loss='mse', metrics=['mae', 'accuracy'])
        return model

    def fit_network_q(self, batch_size):
        self.batch_size = batch_size

    def predict_network_q(self, state):
        self.state = state
        self.q_policy = self.model_q.predict(self.state)
        return self.q_policy

    def update_network_target(self):
        self.network_target.set_weights(self.model_q.get_weights())

    

