from CryptoEnv import CryptoEnvironment, ActionSpace
from CryptoAgent import CryptoAgent
import pandas as pd
import numpy as np
import random
import time
from tqdm import tqdm
import matplotlib.pyplot as plt

# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

original_items = ['event_time','original_open', 'original_close', 'original_high', 'original_low', 'original_volume']

def create_lookback_batches(data, lookback_window=20):

    # create sequences from dataframe
    sequences = []
    for i in range(lookback_window - 1, len(data)):
        sequences.append(data[i:i+lookback_window])

    return np.array(sequences)



def create_reward_history_file(timestamp, columns):
    filename = f"../Results/reward_history_{timestamp}.csv"
    file = open(filename, 'w+')
    i = 0
    with file as f:
        for col in columns:
            if i != 0:
                f.write(",")
            f.write(col)
            i += 1

        f.write("\n")
    return filename

def write_to_file(filename, data):
    with open(filename, "a") as f:
        average_reward, epsilon, balance = data
        f.write(str(average_reward) + "," + str(epsilon) + "," + str(balance) + "\n")


# Receives an index and returns the data for the training and for the environment
def get_train_env_data(data):
    item = pd.DataFrame(data)
    return item[original_items], item.drop(original_items, axis=1)

def main():
    LOOPBACK_WINDOW = 20
    INPUT_SAMPLE_COUNT = 10
    BATCH_SIZE = 64

    EPSILON = 0.98 # Exploration rate
    EPSILON_DECAY = 0.993 # Decay rate
    DISCOUNT = 0.90
    MIN_EPSILON = 0.01 # Minimum exploration rate
    UPDATE_TARGET_INTERVAL = 500

    df = pd.read_csv("../Data/dataset/VETUSDT.csv")
    sequences = create_lookback_batches(df, LOOPBACK_WINDOW)


    env = CryptoEnvironment(sequences, LOOPBACK_WINDOW)
    agent = CryptoAgent(input_shape=(LOOPBACK_WINDOW, 17))
    state = env.reset()

    update_counter = 0
    reward_history = []
    average_reward = 0

    progressbar = tqdm(range(400))

    timestamp = time.strftime("%Y%m%d-%H%M%S")

    filename = create_reward_history_file(timestamp, ['average_reward', 'epsilon', 'balance'])

    for episode in progressbar:
        episode_reward = 0
        step_count = 0

        state = env.reset()

        done = False

        while True:
            if done:
                break
            r = random.random()

            if (r <= EPSILON):
                action = random.choice(list(ActionSpace))
                progressbar.set_description(f"Episode: {episode}, Step: {step_count}, Action: {action}, Random: True, Reward: {episode_reward}, Average Reward: {average_reward}, Epsilon: {EPSILON}")
            else:
                _, data_for_nn = get_train_env_data(state)
                array_state = np.asarray(data_for_nn)
                feature_count = array_state.shape[1]
                q_values = agent.predict_network_q(array_state.reshape(1, LOOPBACK_WINDOW,feature_count))
                progressbar.set_description(f"Episode: {episode}, Step: {step_count}, Action: {q_values}, Random: True, Reward: {episode_reward}, Average Reward: {average_reward}, Epsilon: {EPSILON}")
                action = ActionSpace(np.argmax(q_values))


            new_state, reward, done, info = env.step(action.value)
            if done and step_count < 199:
                reward = -10

            step_count += 1
            step = (state, action.value, reward, new_state, done)

            agent.append_to_replay_memory(step)
            state = new_state
            episode_reward += reward
        
        reward_history.append(episode_reward)
        average_reward = np.mean(reward_history)


        if len(agent.memory) > BATCH_SIZE:
            EPSILON = EPSILON_DECAY * EPSILON
            if EPSILON < MIN_EPSILON:
                EPSILON = MIN_EPSILON

            minibatch_samples = agent.sample_from_replay_memory(BATCH_SIZE)

            mini_batch = []
            for item in minibatch_samples:
                mini_batch.append((get_train_env_data(item[0])[1], item[1], item[2], get_train_env_data(item[3])[1], item[4]))

            mini_batch_states = np.asarray(list(zip(*mini_batch))[0],dtype=float)
            mini_batch_actions = np.asarray(list(zip(*mini_batch))[1], dtype = int)
            mini_batch_rewards = np.asarray(list(zip(*mini_batch))[2], dtype = float)
            mini_batch_next_state = np.asarray(list(zip(*mini_batch))[3],dtype=float)
            mini_batch_done = np.asarray(list(zip(*mini_batch))[4],dtype=bool)

            current_state_q_values = agent.predict_network_q(mini_batch_states)
            y = current_state_q_values

            next_state_q_values = agent.predict_network_target(mini_batch_next_state)

            max_q_next_state = np.max(next_state_q_values, axis=1)

            for i in range(BATCH_SIZE):
                if mini_batch_done[i]:
                    y[i, mini_batch_actions[i]] = mini_batch_rewards[i]
                else:
                    y[i, mini_batch_actions[i]] = mini_batch_rewards[i] + DISCOUNT * max_q_next_state[i]

            agent.fit_network_q(mini_batch_states, y, batch_size=BATCH_SIZE)

        else:
            env.render()
            continue
        if update_counter == UPDATE_TARGET_INTERVAL:
            agent.update_target_network()
            update_counter = 0
        update_counter += 1
        
        reward_history.append(episode_reward)
        write_to_file(filename, [average_reward, EPSILON, env._balance])

    # save last model to Models folder with timestamp
    
    agent.model_q.save(f"../Models/model_{timestamp}.h5")


if __name__ == "__main__":
    main()
