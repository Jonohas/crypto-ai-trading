class Algorithm:
    def __init__(self, environment):
        self.env = environment

    def buy_reward(self):
        return 2

    def sell_reward(self):
        previous_buy = self._get_previous_buy()
        current = self.env._state

        if previous_buy is None:
            return 1

        if previous_buy[-1][2] >= current[-1][2]:
            return -4

        return 3

    def hold_reward(self):
        return 0

    def _get_previous_buy(self):
        for i in range(len(self.env._previous_buy_sell), 0, -1):
            if self.env._previous_buy_sell[i - 1][1] == 0:
                return self.env._previous_buy_sell[i - 1][0]

            else: return None