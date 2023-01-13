import gym
from gym import spaces
import numpy as np

from ActionSpace import ActionSpace
from ActionSpace import Positions

class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, data, arguments, verbose=False):
        super(CryptoEnvironment, self).__init__()

        self._verbose = verbose

        self._data = data

        self._risk = arguments["risk"]  # use max 20% of the account balance

        self._input_shape = ()

        self._look_back_window = arguments["look_back_window"]
        self._look_ahead_window = arguments["look_ahead_window"]

        self._tick = 0 # step count

        self._action_space = spaces.Discrete(len(ActionSpace))
        self._observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._current_candle = None

        self._account_balance = arguments["initial_balance"]
        self._coin_amount = arguments["initial_coin_amount"]
        self._position = Positions.CLOSED

        self._previous_sell_tick = 0
        self._previous_buy_tick = 0 

        self._total_profit = 0
        
        self._profitable_sell_threshold = arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

    def reset(self):
        pass

    def step(self, action):
        pass

    def render(self):
        pass

    def close(self):
        pass