from CryptoEnv_01 import CryptoEnvironment
import pandas as pd

LOOKBACK_WINDOW = 10

def main():
    df = pd.read_csv('./Data/dataset/VETEUR.csv')
    feature_count = len(df.columns)

    env = CryptoEnvironment("VETEUR.csv", input_shape=(LOOKBACK_WINDOW, feature_count), lookback_window=LOOKBACK_WINDOW)

    state = env.reset()
    done = False

    for i in range(10):
        state = env.reset()
        episode_reward = 0

        times_buy = 0
        times_sell = 0
        times_hold = 0

        while not done:

            action = env.action_space.sample()
            next_state, reward, done, _ = env.step(action)
            
            if action == 0:
                times_buy += 1
            
            if action == 1:
                times_hold += 1

            if action == 2:
                times_sell += 1

            episode_reward += reward
            state = next_state

        done = False

        print(state)

        print(f"Episode {i}: {episode_reward}")


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