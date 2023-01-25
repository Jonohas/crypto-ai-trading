import math

class Algorithm:
    def __init__(self, environment):
        self.env = environment

        self._hold_reward_strength = 0.01

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

        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]
        
        current_price = self.env._data.iloc[self.env._tick - 20 :self.env._tick + 20]['original_close'].mean()
        previous_mean = previous_candles['original_close'].mean()
        next_mean = next_candles['original_close'].mean()

        if previous_mean < current_price and current_price < next_mean:
            return True
        
        return False


    def _direction_grade(self):
        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]

        current_price = self.env._data.iloc[self.env._tick - 20 :self.env._tick + 20]['original_close'].mean()

        start_price = previous_candles.iloc[0:5]['original_close'].mean()
        end_price = next_candles.iloc[-5:]['original_close'].mean()

        average_growth = ((current_price - start_price) + (end_price - current_price)) / 2

        return average_growth * 100000 * self._hold_reward_strength




    def _is_downtrend(self):

        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]

        current_price = self.env._data.iloc[self.env._tick - 20 :self.env._tick + 20]['original_close'].mean()
        previous_mean = previous_candles['original_close'].mean()
        next_mean = next_candles['original_close'].mean()

        if previous_mean > current_price and current_price > next_mean:
            return True
        
        return False
    
    def _should_buy(self):
        if self._is_valley():
            return True

        return False

    def _should_sell(self):
        if self._is_peak():
            return True

        return False

    def buy_reward(self):


        buy_action_count = self.env._consecutive_buy_tick

        buy_reward_strength = 1
        # use same method ad sell reward just for buy
        buy_reward = 0

        is_peak = self._is_peak()
        is_valley = self._is_valley()

        direction_growth = self._direction_grade()


        if is_peak and direction_growth > 0:
            buy_reward -= 2 * abs(direction_growth)

        elif is_valley and direction_growth > 0:
            buy_reward += 10 * abs(direction_growth)

        elif is_peak and direction_growth < 0:
            buy_reward -= 4 * abs(direction_growth)

        elif is_valley and direction_growth < 0:
            buy_reward += 5 * abs(direction_growth)



        # return buy_reward * buy_reward_strength
    
        return 0

    def sell_reward(self):
        sell_reward_strength = 1
        sell_reward = 0

        is_peak = self._is_peak()
        is_valley = self._is_valley()

        direction_growth = self._direction_grade()



        if is_peak and direction_growth > 0:
            sell_reward += 5 * abs(direction_growth)


        elif is_valley and direction_growth < 0:
            sell_reward -= 2 * abs(direction_growth)

        elif is_peak and direction_growth < 0:
            sell_reward += 10 * abs(direction_growth)

        elif is_valley and direction_growth > 0:
            sell_reward -= 4 * abs(direction_growth)


        return sell_reward * sell_reward_strength

    def hold_reward(self):
        # check for uptrend only if we have a previous buy
        direction_growth = self._direction_grade()

        step_reward = 0

        is_peak = self._is_peak()
        is_valley = self._is_valley()


        if direction_growth > 0.4:
            step_reward += 2 * abs(direction_growth)

        elif direction_growth < -0.4:
            step_reward += 2 * abs(direction_growth)

        if is_peak or is_valley:
            step_reward -= 12 * abs(direction_growth)

        step_reward -= 10 * abs(direction_growth)

        
        # return step_reward
    
        return 0

    

