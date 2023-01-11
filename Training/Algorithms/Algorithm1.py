class Algorithm:
    def __init__(self, environment):
        self.env = environment

    def _get_previous_buy(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 0:
                return self.env._previous_buy_sell[i - 1][0]
        return None

    def buy_reward(self):
        return 0



    def sell_reward(self):
        previous_buy = self._get_previous_buy()
        current = self.env._state

        if previous_buy is None:
            return 0

        # return on investment (ROI)
        return (((current.iloc[-1][7] - previous_buy.iloc[-1][7]) / previous_buy.iloc[-1][7]) * 100)

    def hold_reward(self):
        # check for uptrend only if we have a previous buy
        previous_buy = self._get_previous_buy()

        previous_step = self.env._get_state(self.env._step_count - 1)
        current = self.env._state
        next_step = self.env._get_state(self.env._step_count + 1)

        # check if we are in a uptrend
        if previous_step.iloc[-1][7] < current.iloc[-1][7] and current.iloc[-1][7] < next_step.iloc[-1][7]:
            # we are in a uptrend
            if previous_buy is None:
                return -1
            return 1
        else:
            # we are in a downtrend
            if previous_buy is None:
                return 1
            return -1

