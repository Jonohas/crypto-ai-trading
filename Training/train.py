# get values from environment variables

# Path: Training/train.py

import pandas as pd
import numpy as np
import os
import sys
from dotenv import load_dotenv

from CryptoEnvironment import CryptoEnvironment

load_dotenv()

class Train():
    def __init__(self, data_path):
        self._data = pd.read_csv(data_path)

        env_risk = float(os.getenv("ENVIRONMENT_RISK_FACTOR"))
        env_initial_balance = float(os.getenv("ENVIRONMENT_INITIAL_BALANCE"))
        env_initial_coin_amount = float(os.getenv("ENVIRONMENT_INITIAL_COIN_AMOUNT"))
        env_look_back_window = int(os.getenv("ENVIRONMENT_LOOK_BACK_WINDOW"))
        env_look_ahead_window = int(os.getenv("ENVIRONMENT_LOOK_AHEAD_WINDOW"))
        env_profitable_sell_threshhold = float(os.getenv("ENVIRONMENT_PROFITABLE_SELL_THRESHHOLD"))
        env_profitable_sell_reward = float(os.getenv("ENVIRONMENT_PROFITABLE_SELL_REWARD"))

        self._verbose = bool(os.getenv("VERBOSE"))

        arguments={
            'risk':  env_risk,
            'initial_balance':  env_initial_balance,
            'initial_coin_amount':  env_initial_coin_amount,
            'look_back_window':  env_look_back_window,
            'look_ahead_window':  env_look_ahead_window,
            'profitable_sell_threshhold':  env_profitable_sell_threshhold,
            'profitable_sell_reward':  env_profitable_sell_reward
        }

        self._env = CryptoEnvironment(self._data, arguments=arguments, verbose=self._verbose)

    def train(self):
        pass


if __name__ == "__main__":
    data_path = os.getenv("DATA_PATH")




    train = Train(data_path)
