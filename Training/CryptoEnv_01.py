import gym
from enum import Enum
from gym import spaces
import numpy as np
import collections
import pandas as pd

from Algorithms.Algorithm1 import Algorithm


INITIAL_BALANCE = 100
INITIAL_COUNT_AMCOUNT = 0

class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2

# observation space looks like this
# 10 candles and their data
# (10, 18)

class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, data_location, lookback_window = 10):
        super(CryptoEnvironment, self).__init__()
        self.data = pd.read_csv("./Data/dataset/", data_location)
        self._org_data = pd.read_csv("./Data/raw/", data_location)

        self._feature_count = len(self.data.columns)

        self._input_shape = (lookback_window, self._feature_count)
        self._lookback_window = lookback_window

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
        return self.data.iloc[step_count * 10: step_count * 10 + 10].values

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

        if len(self.data) - self._items_used < 10:
            return self._state, reward, True, {}

        else:
            next_state = self._get_next_state()
            self._state = next_state
            return next_state, reward, False, {}

    def _buy(self):
        return self._algorithm.buy_reward()

    def _sell(self):
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