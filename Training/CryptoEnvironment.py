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

        self._sequence_length = self._default_arguments["sequence_length"]

        self._look_back_window = self._default_arguments["look_back_window"]
        self._look_ahead_window = self._default_arguments["look_ahead_window"]

        

        self._step_limit = self._default_arguments['step_limit']
        self._tick = self._get_random_tick()

        self._action_space = spaces.Discrete(len(ActionSpace))
        self._observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._current_candle = self._get_state(self._tick)

        self._account_balance = self._default_arguments["initial_balance"]
        self._coin_amount = self._default_arguments["initial_coin_amount"]
        self._position = Positions.CLOSED

        self._consecutive_buy_tick = 0
        self._consecutive_sell_tick = 0

        self._consecutive_threshold = self._default_arguments["consecutive_threshold"]

        self._previous_sell_tick = 0
        self._previous_buy_tick = 0 

        self._previous_action_buy = False

        self._total_profit = 0
        
        self._profitable_sell_threshold = self._default_arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = self._default_arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

    def _get_random_tick(self):
        return random.randint(self._sequence_length, len(self._data) - self._step_limit)

    def random_action(self):
        return random.choice(list(ActionSpace))

    def _get_state(self, tick):
        return self._data.iloc[tick]

    def _get_sequence_env(self, tick):
        return self._data.iloc[tick - self._sequence_length:tick]

    def _get_sequence(self, tick):
        return self._training_data.iloc[tick - self._sequence_length:tick]

    def reset(self):
        self._tick = self._get_random_tick()
        self._current_candle = self._get_state(self._tick)

        self._account_balance = self._default_arguments["initial_balance"]
        self._coin_amount = self._default_arguments["initial_coin_amount"]

        self._consecutive_buy_tick = 0
        self._consecutive_sell_tick = 0

        self._profitable_sell_threshold = self._default_arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = self._default_arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

        self._total_profit = 0
        self._previous_buy_tick = 0
        self._previous_sell_tick = 0
        return self._current_candle

    def step(self, action):
        reward = 0

        done = False

        if action == ActionSpace.BUY.value and self._consecutive_buy_tick <= self._consecutive_threshold:
            reward += self._buy()
            self._previous_buy_tick = self._tick
            self._previous_action_buy = True
        elif action == ActionSpace.BUY.value and self._consecutive_buy_tick > self._consecutive_threshold:
            done = True

        if action == ActionSpace.SELL.value and self._consecutive_sell_tick <= self._consecutive_threshold:
            # if coin amount is 0, we can't sell
            reward += self._sell()
            self._previous_sell_tick = self._tick
            self._previous_action_buy = False

        elif action == ActionSpace.SELL.value and self._consecutive_sell_tick > self._consecutive_threshold:
            done = True

        if action == ActionSpace.HOLD.value:
            reward += self._hold()

        info = {
            "account_balance": self._account_balance,
            "coin_amount": self._coin_amount,
            "profit": self._total_profit,
        }

        if (self._coin_amount * self._current_candle[7] < 20) and self._account_balance < 40:
            done = True
        
        if self._account_balance < 20 and self._coin_amount == 0:
            done = True

        if self._account_balance < 20:
            done = True

        if self._tick >= self._tick + self._step_limit:
            done = True

        
        try:
            next_state = self._get_state(self._tick + 1)

        except IndexError:
            done = True

        self._current_candle = next_state


        self._tick += 1
        return next_state, reward, done, info

    def _buy(self):
        self._consecutive_sell_tick = 0

        self._account_balance -= ((self._account_balance * self._risk) / self._current_candle[7]) * self._current_candle[7]
        self._coin_amount += (self._account_balance * self._risk) / self._current_candle[7]

        self._consecutive_buy_tick += 1
        return self._algorithm.buy_reward()
            
    def _sell(self):
        self._consecutive_buy_tick = 0

        self._account_balance += self._coin_amount * self._current_candle[7]
        # calculate profit
        self._profit = self._account_balance - self._default_arguments["initial_balance"]
        self._coin_amount = 0

        self._consecutive_sell_tick += 1

        return self._algorithm.sell_reward()

    def _hold(self):
        return self._algorithm.hold_reward()

    def render(self):
        pass

    def close(self):
        pass