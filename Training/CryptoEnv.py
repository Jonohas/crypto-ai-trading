import gym
from gym import spaces
import numpy as np
from enum import Enum
import collections
import pandas as pd
import random

from Algorithms.Algorithm1 import Algorithm

# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}


INITIAL_BALANCE = 100
INITIAL_COUNT_AMCOUNT = 0


# create a generator that will return a batch of data
def data_generator(batch_size, files):
    while True:
        random.shuffle(files)
        for file in files:
            data = pd.read_csv(file)
            for i in range(0, len(data), batch_size):
                yield data[i:i+batch_size]


class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2


class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, sequences, lookback_window=20):
        super(CryptoEnvironment, self).__init__()

        self._risk = 0.20
        self.data = sequences

        self._input_shape = self.data[0].shape
        self._lookback_window = self._input_shape[0]

        self._step_count = 0

        self._items_used = 0

        self.action_space = spaces.Discrete(len(ActionSpace))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._state = self._get_state(self._step_count)

        self._algorithm = Algorithm(self)

        self._previous_buy_sell = collections.deque(maxlen=self._lookback_window)

        self._total_profit = 0
        self._profit = 0

        self._balance = INITIAL_BALANCE
        self._coin_amount = INITIAL_COUNT_AMCOUNT

    def _get_state(self, step_count):
        return self.data[step_count]

    def _get_next_state(self):
        self._step_count += 1
        return self._get_state(self._step_count)

    def step(self, action):

        if action == ActionSpace.BUY.value or action == ActionSpace.SELL.value:
            self._previous_buy_sell.append((self._state, action))

        reward = 0

        if action == ActionSpace.BUY.value:
            reward += self._buy()

        if action == ActionSpace.SELL.value:
            reward += self._sell()

        if action == ActionSpace.HOLD.value:
            reward += self._hold()



        # get next state
        self._items_used = self._lookback_window * self._step_count

        # if len(self.data) - self._items_used < self._lookback_window:
        #     return self._state, reward, True, {}

        if self._balance < 20 and self._coin_amount == 0:
            return self._state, reward, True, {}

        

        # else:
        try:
            next_state = self._get_next_state()
        except IndexError:
            return self._state, reward, True, {}

        self._state = next_state
        return next_state, reward, False, {}

    def _buy(self):
        # update balance
        self._balance -= ((self._balance * self._risk) / self._state[-1][7]) * self._state[-1][7]
        self._coin_amount += (self._balance * self._risk) / self._state[-1][7]
        return self._algorithm.buy_reward()

    def _sell(self):
        # sell all coins
        self._balance += self._coin_amount * self._state[-1][7]
        # calculate profit
        self._profit = self._balance - INITIAL_BALANCE
        self._coin_amount = 0

        return self._algorithm.sell_reward()

    def _hold(self):
        return self._algorithm.hold_reward()

    def reset(self):
        self._step_count = 0
        self._state = self._get_state(self._step_count)
        self._balance = INITIAL_BALANCE
        self._coin_amount = INITIAL_COUNT_AMCOUNT

        self._profit = 0
        self._total_profit = 0

        self._previous_buy_sell.clear()
        return self._state

    def render(self):
        pass

    def close(self):
        pass