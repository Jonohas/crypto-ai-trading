from CryptoEnv import CryptoEnvironment, ActionSpace
from CryptoAgent import CryptoAgent
import pandas as pd
import numpy as np
import random
import time
from tqdm import tqdm

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}


import tensorflow
print(tensorflow.__version__)

def create_lookback_batches(data):
    LOOPBACK_WINDOW = 20
    lookback_batches = []

    # loop through data and create batch every 20 samples
    for i in range(0, len(data), LOOPBACK_WINDOW):
        lookback_batches.append(data[i:i+LOOPBACK_WINDOW])

    return lookback_batches



def main():
    LOOPBACK_WINDOW = 20
    INPUT_SAMPLE_COUNT = 10
    BATCH_SIZE = 64

    EPSILON = 0.95 # Exploration rate
    EPSILON_DECAY = 0.999 # Decay rate
    DISCOUNT = 0.90
    MIN_EPSILON = 0.01 # Minimum exploration rate
    UPDATE_TARGET_INTERVAL = 500

    df = pd.read_csv("../Data/dataset/VETUSDT.csv")
    loopback_batches = create_lookback_batches(df)
    loopback_batches = np.array(loopback_batches, dtype=object)
    print(loopback_batches.shape, loopback_batches[0].shape)


    env = CryptoEnvironment(loopback_batches)
    agent = CryptoAgent(input_shape=(LOOPBACK_WINDOW, len(df.columns)))
    state = env.reset()

    update_counter = 0
    reward_history = []

    for episode in tqdm(range(200)):
        episode_reward = 0
        step_count = 0

        state = env.reset()

        done = False

        while not done:
            env.render()
            r = random.randint(0, 2)

            if (r <= EPSILON):
               action = random.choice(list(ActionSpace))
            else:
                array_state = np.asarray(state)
                q_values = agent.predict_network_q(array_state.reshape(1, 20,23))
                action = ActionSpace(np.argmax(q_values))




            new_state, reward, done, info = env.step(action)
            if done and step_count < 199:
                reward = -10

            step_count += 1
            step = (state, action.value, reward, new_state, done)
            agent.append_to_replay_memory(step)
            state = new_state
            episode_reward += reward
        
        reward_history.append(episode_reward)

        if len(agent.memory) > BATCH_SIZE:
            EPSILON = EPSILON_DECAY * EPSILON
            if EPSILON < MIN_EPSILON:
                EPSILON = MIN_EPSILON

            mini_batch = agent.sample_from_replay_memory(BATCH_SIZE)
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

            agent.model_q.fit(mini_batch_states, y, batch_size=BATCH_SIZE, verbose=0)
        else:
            env.render()
            continue
        if update_counter == UPDATE_TARGET_INTERVAL:
            agent.update_target_network()
            update_counter = 0
        update_counter += 1
    print('episodeReward for episode ', episode, '= ', episode_reward, 'with epsilon = ', EPSILON)
    reward_history.append(episode_reward)

if __name__ == "__main__":
    main()
