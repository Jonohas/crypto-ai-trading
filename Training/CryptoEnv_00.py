
from enum import Enum

import numpy as np

from gym import spaces
import gym

from Algorithms.Algorithm1 import Algorithm

import collections

# Use multiple candles as input


BATCH_SIZE = 64
DEFAULT_LOOKBACK_WINDOW = 10
INITIAL_ACCOUNT_BALANCE = 100
INITIAL_COIN_AMOUNT = 0


class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2


class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, data, input_shape = (10, 18), lookback_window = DEFAULT_LOOKBACK_WINDOW):
        super(CryptoEnvironment, self).__init__()
        self.data = data
        self._input_shape = input_shape
        #get first value of data

        self._step_count = 0
        self.update_current_candle()

        self.action_space = spaces.Discrete(len(ActionSpace))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._algorithm = Algorithm(self)
        self._lookback = lookback_window

        self._state_history = collections.deque(maxlen=self._lookback)
        self._action_history = [] # add to this list on buy or sell


        self._done = False

        self._balance = INITIAL_ACCOUNT_BALANCE
        self._coin_amount = INITIAL_COIN_AMOUNT

        self._state = (self._balance, self._coin_amount, self._current_candle)

    def reset(self):
        self._step_count = 0
        self._current_step = None
        self.update_current_candle()

        self._state_history = [] # add to this list every step
        self._action_history = [] # add to this list on buy or sell

        self._previous_step = None
        self._next_step = None
        self._current_step = None
        self._done = False

        self._balance = INITIAL_ACCOUNT_BALANCE
        self._coin_amount = INITIAL_COIN_AMOUNT

        self._state = (self._balance, self._coin_amount, self._current_candle)

        return self._state

    def step(self, action):
        # balance, coin_amount, action, done
        self._current_step = (self._balance, self._coin_amount, action, self._done)

        self._state_history.append(self._current_step)

        if action == ActionSpace.BUY.value or action == ActionSpace.SELL.value:
            # balance, coin_amount, profit
            self._action_history.append(self._current_step)

        reward = 0

        if action == ActionSpace.BUY.value:
            self._buy()
            reward += self._algorithm.buy_reward()

        if action == ActionSpace.SELL.value:
            self._sell()
            reward += self._algorithm.sell_reward()

        if action == ActionSpace.HOLD.value:
            reward += self._algorithm.hold_reward()

        self.update_balance()

        # update current candle


        self._step_count += 1

        self._next_state = (self._balance, self._coin_amount, self._current_candle)
        return self._next_state, reward, self._done, {}


    def _buy(self):
        self._coin_amount = self._balance / self._current_candle['close']

        # balance is rest of balance after buying
        whats_left = self._coin_amount * self._current_candle['close']
        self._balance -= whats_left


    def _sell(self):
        pass




    def render(self):
        pass

    def close(self):
        pass

    def update_balance(self):
        pass

    def calculate_profit(self):
        return self.previous_action['close'] - self.action['close']

    def update_current_candle(self):
        self._current_candle = self.data.iloc[self._step_count]

