class Algorithm:
    def __init__(self, environment):
        self.env = environment

    def _get_previous_buy(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 0:
                return self.env._previous_buy_sell[i - 1][0]
        return None

    def _get_previous_sell(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 1:
                return self.env._previous_buy_sell[i - 1][0]
        return None

    def _is_previous_buy(self):
        previous_action = self.env._previous_buy_sell[-1]
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

    def buy_reward(self):
        if self._is_previous_buy() and not self._is_uptrend():
            return 4

        if self._is_previous_buy() and self._is_uptrend():
            return 2
        
        return -2



    def sell_reward(self):
        previous_buy = self._get_previous_buy()
        current = self.env._state

        if previous_buy is None:
            return 0

        # return on investment (ROI)
        return (((current[-1][7] - previous_buy[-1][7]) / previous_buy[-1][7]) * 100)

    def hold_reward(self):
        # check for uptrend only if we have a previous buy
        previous_buy = self._get_previous_buy()

        previous_step = self.env._get_state(self.env._step_count - 1)
        current = self.env._state
        try:
            next_step = self.env._get_state(self.env._step_count + 1)
        except IndexError:
            return 0

        # check if we are in a uptrend
        if previous_step[-1][7] < current[-1][7] and current[-1][7] < next_step[-1][7]:
            # we are in a uptrend
            if previous_buy is None:
                return -10  
            return 20
        else:
            # we are in a downtrend
            if previous_buy is None:
                return 20
            return -10

