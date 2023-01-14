import gym
from gym import spaces
import numpy as np
import random

from ActionSpace import ActionSpace
from ActionSpace import Positions
from Algorithms.CrypoAlgorithm import Algorithm

class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, data, training_data, arguments, input_shape, log_dir, verbose=False):
        super(CryptoEnvironment, self).__init__()

        self._algorithm = Algorithm(self)

        self._default_arguments = arguments
        self.log_dir = log_dir
        self._verbose = verbose

        self._data = data
        self._training_data = training_data

        self._risk = arguments["risk"]  # use max 20% of the account balance

        self._input_shape = ()

        self._look_back_window = self._default_arguments["look_back_window"]
        self._look_ahead_window = self._default_arguments["look_ahead_window"]

        self._tick = self._default_arguments["look_back_window"] # step count

        self._action_space = spaces.Discrete(len(ActionSpace))
        self._observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._current_candle = self._get_state(self._tick)

        self._account_balance = self._default_arguments["initial_balance"]
        self._coin_amount = self._default_arguments["initial_coin_amount"]
        self._position = Positions.CLOSED

        self._previous_sell_tick = 0
        self._previous_buy_tick = 0 

        self._previous_action_buy = False

        self._total_profit = 0
        
        self._profitable_sell_threshold = self._default_arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = self._default_arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

    def random_action(self):
        return random.choice(list(ActionSpace))

    def _get_state(self, tick):
        return self._data.iloc[tick]

    def _get_sequence_env(self, tick):
        return self._data.iloc[tick - self._look_back_window:tick]

    def _get_sequence(self, tick):
        return self._training_data.iloc[tick - self._look_back_window:tick]

    def reset(self):
        self._tick = self._default_arguments["look_back_window"]
        self._current_candle = self._get_state(self._tick)

        self._account_balance = self._default_arguments["initial_balance"]
        self._coin_amount = self._default_arguments["initial_coin_amount"]

        self._profitable_sell_threshold = self._default_arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = self._default_arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

        self._total_profit = 0
        self._previous_buy_tick = 0
        self._previous_sell_tick = 0
        return self._current_candle

    def step(self, action):
        reward = 0



        if action == ActionSpace.BUY.value:
            self._previous_buy_tick = self._tick
            self._previous_action_buy = True
            reward += self._buy()

        if action == ActionSpace.SELL.value:
            self._previous_sell_tick = self._tick
            self._previous_action_buy = False
            reward += self._sell()

        if action == ActionSpace.HOLD.value:
            reward += self._hold()

        if (self._coin_amount * self._current_candle[7] < 20) and self._account_balance < 40:
            return self._current_candle, reward, True, {}
        
        if self._account_balance < 20 and self._coin_amount == 0:
            return self._current_candle, reward, True, {}

        if self._account_balance < 20:
            return self._current_candle, reward, True, {}

        
        try:
            next_state = self._get_state(self._tick + 1)

        except IndexError:
            return self._current_candle, reward, True, {}

        self._current_candle = next_state


        self._tick += 1
        return next_state, reward, False, {}

    def _buy(self):
        self._account_balance -= ((self._account_balance * self._risk) / self._current_candle[7]) * self._current_candle[7]
        self._coin_amount += (self._account_balance * self._risk) / self._current_candle[7]
        return self._algorithm.buy_reward()
            
    def _sell(self):
        self._account_balance += self._coin_amount * self._current_candle[7]
        # calculate profit
        self._profit = self._account_balance - self._default_arguments["initial_balance"]
        self._coin_amount = 0

        return self._algorithm.sell_reward()

    def _hold(self):
        return self._algorithm.hold_reward()

    def render(self):
        pass

    def close(self):
        pass