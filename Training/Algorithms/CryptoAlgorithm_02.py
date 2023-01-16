

class Algorithm:
    def __init__(self, environment):
        self.env = environment

    def buy_reward(self):

        return 10

    def sell_reward(self):

        # calculate return on investment
        return_on_investment = (self.env._account_balance - self.env._default_arguments["initial_balance"]) / self.env._default_arguments["initial_balance"] * 100

        return return_on_investment

        return 10

    def hold_reward(self):

        return 10

    

