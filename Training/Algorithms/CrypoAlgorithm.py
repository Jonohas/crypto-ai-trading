

class Algorithm:
    def __init__(self, environment):
        self.env = environment

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

        if self.env._tick == self.env._sequence_length:
            return False

        previous_step = self.env._get_sequence_env(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False

        if previous_step.iloc[-1]['original_close'] < current.iloc[-1]['original_close'] and current.iloc[-1]['original_close']  > next_step['original_close']:
            return True

        return False

    def _is_valley(self):
        current = self.env._get_sequence_env(self.env._tick)

        if self.env._tick == self.env._sequence_length:
            return False

        previous_step = self.env._get_sequence_env(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False

        if previous_step.iloc[-1]['original_close'] > current.iloc[-1]['original_close'] and current.iloc[-1]['original_close']  < next_step['original_close']:
            return True

        return False


    def _is_uptrend(self):

        # check if last 100 to next 50 candles are uptrend

        # perdiod_candles = self.env._data.iloc[self.env._tick - 100, self.env._tick + 50]
        # period_mean = perdiod_candles['original_close'].mean()
        
        current = self.env._get_sequence_env(self.env._tick)

        if self.env._tick == self.env._sequence_length:
            return False

        previous_step = self.env._get_sequence_env(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False

        # print(previous_step.tail(1)['original_close'], current.tail(1)['original_close'], next_step['original_close'])
        
        if previous_step.iloc[-1]['original_close'] < current.iloc[-1]['original_close'] and current.iloc[-1]['original_close']  < next_step['original_close']:
            return True
        return False



    def _is_downtrend(self):
        current = self.env._get_sequence_env(self.env._tick)

        if self.env._tick == self.env._sequence_length:
            return False

        previous_step = self.env._get_sequence_env(self.env._tick - 1)
        

        try:
            next_step = self.env._get_state(self.env._tick + 1)
        except IndexError:
            return False


        if previous_step.iloc[-1]['original_close'] > current.iloc[-1]['original_close'] and current.iloc[-1]['original_close']  > next_step['original_close']:
            return True
        return False


    def buy_reward(self):

        step_reward = 0

        current_price = self.env._current_candle[7]
        lookback_tick = self.env._tick - self.env._look_back_window


        # try:
        #     last_buy_price = self.env._get_state(self._get_previous_buy())['original_close']
        # except Exception as e:
        #     return 0

        # if not self.env._previous_action_buy:

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
            # print("CP > TMP", rr)
            # punishment for buying too high
            step_reward += rr


        if current_price < temp_max_price:
            rr = ((temp_max_price - current_price) / current_price) * 100
            # print("CP < TMP", rr)
            # reward for buying at low point
            # increase to prevent piramidding
            step_reward += rr
            
        del temp_max_price
        del temp_min_price

        # else:
        #     testreward = ((last_buy_price - current_price) / current_price) * 100
        #     step_reward += testreward


        del current_price

        # print("Buy step reward: ", step_reward * 100)

        return step_reward * 100

    def sell_reward(self):
        # on sell check if it is higher than the previous sell


        step_reward = 0

        current_price = self.env._current_candle[7]

        lookback_tick = self.env._tick - self.env._look_back_window

        # try:
        #     previous_buy = self._get_previous_buy()
        # except:
        #     return 0

        # try:

        #     previous_buy = self._get_previous_buy()
        #     last_buy_price = self.env._get_state(previous_buy)[7]
        # except:
        #     return 0
 

        step_reward = 0


        # if self.env._previous_action_buy:

        # if last_buy_price * (1 + (self.env._profitable_sell_threshold / 100)) >= current_price:
        #     step_reward += self.env._profitable_sell_reward
            
        # else:
        #     step_reward += self.env._none_profitable_sell_reward

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

        ipb = self.env._previous_action_buy

        # is_up = self._is_uptrend()
        # is_down = self._is_downtrend()
        is_peak = self._is_peak()
        is_valley = self._is_valley()


        # if is_up and ipb:
        #     return 50

        # elif is_down and ipb:
        #     return -70

        # elif is_up and not ipb:
        #     return -70

        # elif is_down and not ipb:
        #     return 50

        if is_peak or is_valley:
            return -10

        return 10

    

