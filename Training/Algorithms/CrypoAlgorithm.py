

class Algorithm:
    def __init__(self, environment):
        self.env = environment

        self._hold_reward_strength = 0.82

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

        previous_steps = self.env._data.iloc[self.env._tick - 10:self.env._tick - 1]
        following_steps = self.env._data.iloc[self.env._tick + 1 :self.env._tick + 10]

        current_price = current.iloc[-1]['original_close']

        if current_price > previous_steps['original_close'].max() and current_price > following_steps['original_close'].max():
            return True

        return False


    def _is_valley(self):
        current = self.env._get_sequence_env(self.env._tick)

        previous_steps = self.env._data.iloc[self.env._tick - 10:self.env._tick - 1]
        following_steps = self.env._data.iloc[self.env._tick + 1 :self.env._tick + 10]

        current_price = current.iloc[-1]['original_close']

        if current_price < previous_steps['original_close'].min() and current_price < following_steps['original_close'].min():
            return True

        return False


    def _is_uptrend(self):

        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]
        
        current = self.env._get_sequence_env(self.env._tick)
        current_price = current.iloc[-1]['original_close']
        previous_mean = previous_candles['original_close'].mean()
        next_mean = next_candles['original_close'].mean()

        if previous_mean < current_price and current_price < next_mean:
            return True
        
        return False


    def _direction_grade(self):
        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]

        current = self.env._get_sequence_env(self.env._tick)
        current_price = current.iloc[-1]['original_close']

        start_price = previous_candles.iloc[0:5]['original_close'].mean()
        end_price = next_candles.iloc[-5:]['original_close'].mean()

        average_growth = ((current_price - start_price) + (end_price - current_price)) / 2

        return average_growth * 100000 * self._hold_reward_strength




    def _is_downtrend(self):

        previous_candles = self.env._data.iloc[self.env._tick - 100:self.env._tick]
        next_candles = self.env._data.iloc[self.env._tick:self.env._tick + 50]
        
        current = self.env._get_sequence_env(self.env._tick)
        current_price = current.iloc[-1]['original_close']
        previous_mean = previous_candles['original_close'].mean()
        next_mean = next_candles['original_close'].mean()

        if previous_mean > current_price and current_price > next_mean:
            return True
        
        return False


    def buy_reward(self):
        buy_count = self.env._consecutive_buy_tick


        step_reward = 0

        step_reward -= buy_count

        current_price = self.env._current_candle[7]
        lookback_tick = self.env._tick - self.env._look_back_window


        temp_max_price = current_price
        temp_min_price = current_price

        for tick in range(lookback_tick, self.env._tick + self.env._look_ahead_window):
            
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
            rr = ((temp_min_price - current_price) / current_price) * 100
            step_reward += rr


        if current_price < temp_max_price:
            rr = ((temp_max_price - current_price) / current_price) * 100
            step_reward += rr
            
        del temp_max_price
        del temp_min_price
        del current_price

        return step_reward * 100

    def sell_reward(self):
        sell_count = self.env._consecutive_sell_tick


        step_reward = 0

        step_reward -= sell_count

        current_price = self.env._current_candle[7]

        lookback_tick = self.env._tick - self.env._look_back_window

        temp_max_price = current_price
        temp_min_price = current_price

        for tick in range(lookback_tick, self.env._tick + self.env._look_ahead_window):
            if tick >= len(self.env._data) - 1:
                continue
            price = self.env._get_state(tick)[7]

            if price > current_price:
                # good
                if price > temp_max_price:
                    temp_max_price = price

            if price < current_price:
                # bad, means this buy is sub-optimal
                if price < temp_min_price:
                    temp_min_price = price

            del price


        if current_price < temp_max_price:
            # punishment for selling too low
            step_reward += ((current_price - temp_max_price) / temp_max_price) * 100

        if current_price > temp_min_price:
            # reward for selling above lowest point
            step_reward += ((current_price - temp_min_price) / temp_min_price) * 100


        del temp_max_price
        del temp_min_price

        # else:
        #     step_reward += ((last_buy_price - current_price) / current_price) * 100

        del current_price

        # print("Sell step reward: ", step_reward * 100)

        return step_reward * 100

    def hold_reward(self):
        # check for uptrend only if we have a previous buy
        direction_growth = self._direction_grade()

        is_up = self._is_uptrend()
        is_down = self._is_downtrend()
        is_peak = self._is_peak()
        is_valley = self._is_valley()

        reward = 0

        if is_up:
            reward += 2 * abs(direction_growth)

        elif is_down:
            reward += 2 * abs(direction_growth)

        if is_peak or is_valley:
            reward -= 1 * abs(direction_growth)

        if reward == 0:
            reward = abs(direction_growth)

        
        return reward

    

