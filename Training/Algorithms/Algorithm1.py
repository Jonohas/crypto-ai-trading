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
        return 0

