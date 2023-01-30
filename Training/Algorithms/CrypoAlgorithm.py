import math

from ActionSpace import ActionSpace, Positions
import numpy as np

class Algorithm:
    def __init__(self, environment):
        self.env = environment

        self._hold_reward_strength = 0.6

    def _get_previous_buy(self):
        previous_buy_tick = self.env._previous_buy_tick
        if previous_buy_tick == 0:
            return None

        return self.env._previous_buy_tick

    def _get_previous_sell(self):
        previous_sell_tick = self.env._previous_sell_tick
        if previous_sell_tick == 0:
            return None

        return self.env._previous_sell_tick
    

    def _coming_buy_sell_point(self):
        # returns the closeness of a buy or sell point between 0 and 1

        current = self.env._get_state(self.env._tick)
        coming_candles = self.env._data.iloc[self.env._tick + 1 :self.env._tick + 10].copy()

        previous_action_sell = self.env._previous_action_sell
        previous_action_buy = self.env._previous_action_buy

        coming_candles = np.array(coming_candles['original_close'])

        max_index = np.argmax(coming_candles)
        min_index = np.argmin(coming_candles)
        # print(' ')

        current_price = current['original_close']

        # max_index= coming_candles['original_close'].idxmax()
        # min_index = coming_candles['original_close'].idxmin()

        # coming_maximum = (max_index - self.env._start_tick - self.env._tick)
        # coming_minimum = (min_index - self.env._start_tick - self.env._tick)

        # print(self.env._tick, self.env._start_tick, coming_candles.shape, min_index, max_index)

        return_value = 0

        if previous_action_sell == True:
            # if down trend check for coming minimum

            if self._is_downtrend():
                return_value += (30 - min_index) / 30
                # print('downtrend', return_value)

            if self._is_uptrend():
                return_value -= (30 - max_index) / 30
                # print('uptrend', return_value)

        elif previous_action_buy == True:
            # if up trend check for coming maximum
            if self._is_uptrend():
                return_value += (30 - max_index) / 30
                # print('uptrend', return_value)

            if self._is_downtrend():
                return_value -= (30 - min_index) / 30
                # print('downtrend', return_value)




        # if self.env._position == Positions.OPEN:
        #     # look at coming maximum
        #     return_value = (30 - max_index) / 30

        # else:
        #     return_value = (30 - min_index) / 30
        #     # look at coming minimum

        if return_value == 1:
            return 0
        
        return return_value


    



    def _is_peak(self):
        current = self.env._get_sequence_env(self.env._tick)

        previous_steps = self.env._data.iloc[self.env._tick - 3:self.env._tick - 1]
        following_steps = self.env._data.iloc[self.env._tick + 1 :self.env._tick + 3]

        current_price = current.iloc[-1]['original_close']

        if current_price > previous_steps['original_close'].max() and current_price > following_steps['original_close'].max():
            return True

        return False


    def _is_valley(self):
        current = self.env._get_sequence_env(self.env._tick)

        previous_steps = self.env._data.iloc[self.env._tick - 3:self.env._tick - 1]
        following_steps = self.env._data.iloc[self.env._tick + 1 :self.env._tick + 3]

        current_price = current.iloc[-1]['original_close']

        if current_price < previous_steps['original_close'].min() and current_price < following_steps['original_close'].min():
            return True

        return False

    def _is_uptrend(self):
        
        current = self.env._get_state(self.env._tick)

        if self.env._tick == self.env._look_back_window:
            return False

        previous_step = self.env._get_state(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False

        # print(previous_step.tail(1)['original_close'], current.tail(1)['original_close'], next_step['original_close'])
        
        if previous_step['original_close'] < current['original_close'] and current['original_close']  < next_step['original_close']:
            return True
        return False



    def _is_downtrend(self):
        current = self.env._get_state(self.env._tick)

        if self.env._tick == self.env._look_back_window:
            return False

        previous_step = self.env._get_state(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False


        if previous_step['original_close'] > current['original_close'] and current['original_close']  > next_step['original_close']:
            return True
        return False
    
    def _direction_grade(self):
        previous_candles = self.env._data.iloc[self.env._tick - self.env._look_back_window:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + self.env._look_ahead_window]

        current = self.env._get_sequence_env(self.env._tick)
        current_price = current.iloc[-1]['original_close']

        start_price = previous_candles.iloc[0:5]['original_close'].mean()
        end_price = next_candles.iloc[-5:]['original_close'].mean()

        average_growth = ((current_price - start_price) + (end_price - current_price)) / 2

        return average_growth * 100000 * self._hold_reward_strength




    def buy_reward(self):
        consec_buys = self.env._consecutive_buy_tick

        step_reward = 0

        current_price = self.env._current_candle[7]

        
        previous_sell = self._get_previous_sell()

        if previous_sell is None:
            return 0

        try:
            last_buy_price = self.env._get_state(self._get_previous_buy())['original_close']
        except Exception as e:
            return 0

        if not self.env._previous_action_buy:

            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_sell, self.env._tick + self.env._look_ahead_window):
                
                if tick >= len(self.env._data) - 1:
                    continue

                price = self.env._get_state(tick)['original_close']

                if price > current_price:
                    # good
                    if price > temp_max_price:
                        temp_max_price = price

                if price < current_price:
                    # bad, means this buy is sub-optimal
                    if price < temp_min_price:
                        temp_min_price = price

                del price
                

            if current_price > temp_min_price:
                # punishment for buying too high
                step_reward += ((temp_min_price - current_price) / current_price) * 100

            if current_price < temp_max_price:
                # reward for buying at low point
                # increase to prevent piramidding
                step_reward += ((temp_max_price - current_price) / current_price) * 100
                
            del temp_max_price
            del temp_min_price

        else:
            step_reward += ((last_buy_price - current_price) / current_price) * 100


        del current_price

        return step_reward * 100

    def sell_reward(self, profit):
        # on sell check if it is higher than the previous sell
        consec_sells = self.env._consecutive_sell_tick

        step_reward = 0

        if consec_sells > 0 and profit == 0:
            step_reward -= 3 ** math.log(consec_sells)



        current_price = self.env._current_candle[7]

        try:
            previous_buy = self._get_previous_buy()
        except:
            return 0

        try:

            previous_buy = self._get_previous_buy()
            last_buy_price = self.env._get_state(previous_buy)[7]
        except:
            return 0




        if not self.env._previous_action_buy:

            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_buy, self.env._tick + self.env._look_ahead_window):
                if tick >= len(self.env._data) - 1:
                    continue
                price = self.env._get_state(tick)['original_close']

                if price > current_price:
                    if price < temp_min_price:
                        temp_min_price = price


                if price < current_price:
                    # bad, means this buy is sub-optimal
                                        # good
                    if price > temp_max_price:
                        temp_max_price = price

                del price


            if current_price < temp_max_price:
                # punishment for selling too low
                value = ((current_price - temp_max_price) / temp_max_price) * 100
                step_reward -= value

            if current_price > temp_min_price:
                # reward for selling above lowest point
                step_reward += ((current_price - temp_min_price) / temp_min_price) * 100


            del temp_max_price
            del temp_min_price

        else:
            if profit == 0:
                profit = 0
            else:
                step_reward += 10 * profit

        del current_price


        return step_reward * 100

    def hold_reward(self):
        # check for uptrend only if we have a previous buy
        direction_growth = self._direction_grade()

        is_up = self._is_uptrend()
        is_down = self._is_downtrend()
        is_peak = self._is_peak()
        is_valley = self._is_valley()

        coming_sell_buy_point = self._coming_buy_sell_point()

        reward = 0

        if is_up:
            reward += 2 * abs(direction_growth)

        elif is_down:
            reward += 2 * abs(direction_growth)

        if is_peak or is_valley:
            reward -= 4 * abs(direction_growth)

        if reward == 0:
            reward = abs(direction_growth)

        if coming_sell_buy_point:
            reward += 100 * coming_sell_buy_point

        
        return reward
