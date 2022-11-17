
from enum import Enum

import numpy as np

from gym import spaces
import gym

# Use multiple candles as input


BATCH_SIZE = 64

INITIAL_ACCOUNT_BALANCE = 100


class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2


class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, data):
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

