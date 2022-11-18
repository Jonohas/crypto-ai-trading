from CryptoEnv_00 import CryptoEnvironment
import pandas as pd

LOOKBACK_WINDOW = 10

def main():
    df = pd.read_csv('Data/dataset/VETEUR.csv')

    print(df.head(15))

    # # remove time from data
    # df = df.drop(columns=['event_time'])

    # # print of features
    # feature_count = len(df.columns)
    

    # env = CryptoEnvironment(df, input_shape=(LOOKBACK_WINDOW, feature_count), lookback_window=LOOKBACK_WINDOW)
    # state = env.reset()

    # for i in range(10):
    #     action = env.action_space.sample()
    #     next_state, reward, done, _ = env.step(action)
    #     print(f"Action: {action} | Reward: {reward} | Done: {done} | Balance {next_state[0]} | Coin amount: {next_state[1]}")
    #     state = next_state


if __name__ == '__main__':
    main()