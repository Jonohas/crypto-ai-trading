import gym
from gym import spaces
import numpy as np
import random

from ActionSpace import ActionSpace
from ActionSpace import Positions
from Algorithms.CrypoAlgorithm import Algorithm

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import pandas as pd

class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, data, training_data, arguments, input_shape, log_dir, verbose=False):
        super(CryptoEnvironment, self).__init__()

        

        plt.ion()

        self.fig = plt.figure(figsize=(20, 10))
        self.grid = plt.GridSpec(3, 2)
        self.fig.tight_layout(pad=3)

        self._ax1 = self.fig.add_subplot(self.grid[0:2, :2])
        # self._ax1_twin = self._ax1.twinx()

        self._ax2 = self.fig.add_subplot(self.grid[2:3, :2])

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
        self._start_tick = self._tick
        
        self._x_values = [i for i in range(self._step_limit)]



        self._action_space = spaces.Discrete(len(ActionSpace))
        self._observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=self._input_shape, dtype=np.double)

        self._current_candle = self._get_state(self._tick)

        self._account_balance = self._default_arguments["initial_balance"]
        self._coin_amount = self._default_arguments["initial_coin_amount"]
        self._position = Positions.CLOSED

        self._consecutive_buy_tick = 0
        self._consecutive_sell_tick = 0
        self._consecutive_hold_tick = 0

        self._consecutive_threshold = self._default_arguments["consecutive_threshold"]

        self._previous_sell_tick = 0
        self._previous_buy_tick = 0 

        self._previous_action_buy = False

        self._total_profit = 0
        
        self._profitable_sell_threshold = self._default_arguments["profitable_sell_threshhold"] # 1% profit
        self._profitable_sell_reward = self._default_arguments["profitable_sell_reward"]
        self._none_profitable_sell_reward = -self._profitable_sell_reward

        self._action_list = {
            "buy": [],
            "hold": [],
            "sell": []
        }

    def _get_random_tick(self):
        self._offset = random.randint(self._sequence_length, self._sequence_length + self._step_limit)
        return self._offset

    def random_action(self):
        return random.choice(list(ActionSpace))

    def _get_state(self, tick):
        return self._data.iloc[tick]

    def _get_sequence_env(self, tick):
        return self._data.iloc[tick - self._sequence_length:tick]

    def _get_sequence(self, tick):
        return self._training_data.iloc[tick - self._sequence_length:tick]

    def reset(self):
        self._action_list = {
            "buy": [],
            "hold": [],
            "sell": []
        }
        self._tick = self._get_random_tick()
        self._start_tick = self._tick
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
    
    def _plot_data(self, start_tick, end_tick, episode):

        data = self._data.iloc[start_tick:end_tick]
        self._ax1.clear()
        self._ax2.clear()

        balance_patch = mpatches.Patch(color='red', label='Balance: ' + str(round(self._account_balance,2)))
        coin_patch = mpatches.Patch(color='blue', label='Coin Amount: ' + str(round(self._coin_amount,2)))

        self._ax1.set_title(f"Episode: {episode}")
        

        price, = self._ax1.plot(self._x_values, data["original_close"], label="Price")

        # volume, = self._ax1.plot(self._x_values, data["volume"], label="Volume", color="red")

        handles = [balance_patch, coin_patch, price]

        buys = pd.DataFrame(self._action_list['buy'])

        buys_random = buys[buys['random'] == True]
        buys_not_random = buys[buys['random'] == False]

        sells = pd.DataFrame(self._action_list['sell'])

        sells_random = sells[sells['random'] == True]
        sells_not_random = sells[sells['random'] == False]


        holds = pd.DataFrame(self._action_list['hold'])

        holds_random = holds[holds['random'] == True]
        holds_not_random = holds[holds['random'] == False]

        if len(self._action_list['buy']) > 0:
            b, = self._ax1.plot(buys_not_random['tick'], buys_not_random['original_close'], 's', color='cyan', label="Buy")
            br, = self._ax1.plot(buys_random['tick'], buys_random['original_close'], '^', color='cyan', label="Buy Random")
            breward = self._ax2.bar(buys['tick'], buys['reward'], bottom=None, align='center', color='cyan', label="Reward")
            handles.append(b)
            handles.append(br)

        if len(self._action_list['hold']) > 0:
            h, = self._ax1.plot(holds_not_random['tick'], holds_not_random['original_close'], 's', color='black', label="Hold")
            hr, = self._ax1.plot(holds_random['tick'], holds_random['original_close'], '^', color='black', label="Hold Random")
            hreward = self._ax2.bar(holds['tick'], holds['reward'], bottom=None, align='center', color='black', label="Reward")
            handles.append(h)
            handles.append(hr)

        if len(self._action_list['sell']) > 0:
            s, = self._ax1.plot(sells_not_random['tick'], sells_not_random['original_close'], 's', color='magenta', label="Sell")
            sr, = self._ax1.plot(sells_random['tick'], sells_random['original_close'], '^', color='magenta', label="Sell Random")
            sreward = self._ax2.bar(sells['tick'], sells['reward'], bottom=None, align='center', color='magenta', label="Reward")
            handles.append(s)
            handles.append(sr)

        self._ax1.set_ylabel('Price')
        self._ax1.set_xlabel('Time')

        
        self._ax1.legend(handles=handles)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def step(self, action, random):
        reward = 0

        done = False

        temp_state = self._get_state(self._tick).copy()
        temp_state['tick'] = int(self._tick - self._offset)
        temp_state['random'] = random


        if action == ActionSpace.BUY.value:
            reward += self._buy()
            temp_state['reward'] = reward
            self._action_list['buy'].append(temp_state)
            self._previous_buy_tick = self._tick
            self._previous_action_buy = True

        if action == ActionSpace.SELL.value:
            # if coin amount is 0, we can't sell
            reward += self._sell()
            temp_state['reward'] = reward
            self._action_list['sell'].append(temp_state)
            self._previous_sell_tick = self._tick
            self._previous_action_buy = False

        if action == ActionSpace.HOLD.value:
            reward += self._hold()
            temp_state['reward'] = reward
            self._action_list['hold'].append(temp_state)

        info = {
            "account_balance": self._account_balance,
            "coin_amount": self._coin_amount,
            "profit": self._total_profit,
        }

        if self._coin_amount * self._current_candle[7] + self._account_balance < 0:
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
        self._consecutive_hold_tick = 0

        self._account_balance -= ((self._account_balance * self._risk) / self._current_candle[7]) * self._current_candle[7]
        self._coin_amount += (self._account_balance * self._risk) / self._current_candle[7]

        self._consecutive_buy_tick += 1
        return self._algorithm.buy_reward()
            
    def _sell(self):
        self._consecutive_buy_tick = 0
        self._consecutive_hold_tick = 0

        prev_account_balance = self._account_balance

        self._account_balance += self._coin_amount * self._current_candle[7]
        # calculate profit
        self._profit = prev_account_balance - self._account_balance
        self._coin_amount = 0

        self._consecutive_sell_tick += 1

        return self._algorithm.sell_reward()

    def _hold(self):
        self._consecutive_buy_tick = 0
        self._consecutive_sell_tick = 0
        self._consecutive_hold_tick += 1
        return self._algorithm.hold_reward()

    def render(self, episode):
        try:
            self._plot_data(self._start_tick, self._start_tick + self._step_limit, episode)
        except Exception as e:
            print("\n")
            print("=====================================")
            print("\n")
            print(e)
            print("\n")
            print("=====================================")
            print("\n")

    def close(self):
        pass