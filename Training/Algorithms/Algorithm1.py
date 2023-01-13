class Algorithm:
    def __init__(self, environment):
        self.env = environment



    def _get_previous_buy(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 0:
                return self.env._previous_buy_sell[i - 1]
        return None

    def _get_previous_sell(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 2:
                return self.env._previous_buy_sell[i - 1]
        return None

    def _is_previous_buy(self):
        previous_action = None
        try:
            previous_action = self.env._previous_buy_sell[-1]
        except IndexError:
            return False

        if previous_action[1] == 0:
            # previous action was a buy
            return True
        return False


    # zou ik de uptrend bepalen op basis van mijn volledige sequence of gewoon de vorige huidige en volgende?
    def _is_uptrend(self):
        previous_step = self.env._get_state(self.env._step_count - 1)
        current = self.env._state

        try:
            next_step = self.env._get_state(self.env._step_count + 1)
        except IndexError:
            return 0

        if previous_step[-1][7] < current[-1][7] and current[-1][7] < next_step[-1][7]:
            return True
        return False


    def _is_downtrend(self):
        previous_step = self.env._get_state(self.env._step_count - 1)
        current = self.env._state

        try:
            next_step = self.env._get_state(self.env._step_count + 1)
        except IndexError:
            return 0

        if previous_step[-1][7] > current[-1][7] and current[-1][7] > next_step[-1][7]:
            return True
        return False




    def buy_reward(self):

        step_reward = 0

        current_price = self.env._state[-1][7]

        try:
            previous_sell = self._get_previous_sell()[2]
        except:
            return 0

        try:
            last_buy_price = self._get_previous_buy()[0][-1][7]
        except:
            return 0

        if not self._is_previous_buy():

            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_sell, self.env._step_count + self.env._lookahead_window):
                if tick >= len(self.env.data) - 1:
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

        # if self._is_previous_buy() and not self._is_uptrend():
        #     return 0

        # if self._is_previous_buy() and self._is_uptrend():
        #     return -5
        
        # return -2



    def sell_reward(self):
        # on sell check if it is higher than the previous sell


        step_reward = 0

        current_price = self.env._state[-1][7]

        try:
            previous_buy = self._get_previous_buy()[2]
        except:
            return 0

        try:
            last_buy_price = self._get_previous_buy()[0][-1][7]
        except:
            return 0


        step_reward = 0

        if not self._is_previous_buy():

            if last_buy_price * (1 + (self.env._profitable_sell_threshold / 100)) >= current_price:
                step_reward += self.env._profitable_sell_reward
                
            else:
                step_reward += self.env._non_profitable_sell_punishment

            temp_max_price = current_price
            temp_min_price = current_price

            for tick in range(previous_buy, self.env._step_count + self.env._lookahead_window):
                if tick >= len(self.env.data) - 1:
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

        # try:
        #     previous_buy = self._get_previous_buy()[0]
        # except:
        #     return 0

        # current = self.env._state

        # if previous_buy is None:
        #     return 0

        # ROI = ((current[-1][7] - previous_buy[-1][7]) / previous_buy[-1][7]) * 10000

        # return ROI

    def hold_reward(self):
        # check for uptrend only if we have a previous buy

        ipb = self._is_previous_buy()

        if self._is_uptrend() and ipb:
            return 20

        elif self._is_downtrend() and ipb:
            return -20

        elif self._is_uptrend() and not ipb:
            return -20

        elif self._is_downtrend() and not ipb:
            return 20

        return 0


