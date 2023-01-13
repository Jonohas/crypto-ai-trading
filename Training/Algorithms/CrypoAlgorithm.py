

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


    def _is_uptrend(self):
        
        current = self.env._get_sequence_env(self.env._tick)

        if self.env._tick == self.env._look_back_window:
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

        if self.env._tick == self.env._look_back_window:
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


        try:
            previous_sell = self._get_previous_sell()
        except:
            return 0

        try:
            last_buy_price = self._get_previous_buy()[7]
        except:
            return 0

        if not self.env._previous_action_buy:
            
            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_sell, self.env._tick + self.env._look_ahead_window):
                if tick >= len(self.env._data) - 1:
                    continue
                price = self.env._get_state(tick)[-1][7]



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

    def sell_reward(self):
        # on sell check if it is higher than the previous sell


        step_reward = 0

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


        step_reward = 0

        if not self.env._previous_action_buy:

            if last_buy_price * (1 + (self.env._profitable_sell_threshold / 100)) >= current_price:
                step_reward += self.env._profitable_sell_reward
                
            else:
                step_reward += self.env._non_profitable_sell_punishment

            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_buy, self.env._tick + self.env._look_ahead_window):
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

        else:
            step_reward += ((last_buy_price - current_price) / current_price) * 100

        del current_price

        return step_reward * 100

    def hold_reward(self):
        print("hold reward")
        # check for uptrend only if we have a previous buy

        ipb = self.env._previous_action_buy

        is_up = self._is_uptrend()
        is_down = self._is_downtrend()

        print("is_up: ", is_up)
        print("is_down: ", is_down)

        if is_up and ipb:
            return 20

        elif is_down and ipb:
            return -20

        elif is_up and not ipb:
            return -20

        elif is_down and not ipb:
            return 20

        return 0

