from CryptoEnvironment import CryptoEnvironment,ActionSpace, CryptoAgent
import pandas as pd
import random
import numpy as np




def main():
    df = pd.read_csv('Data/dataset/VETEUR.csv')

    INPUT_SAMPLE_COUNT = 10
    LOOKBACK_WINDOW = 10
    BATCH_SIZE = 64

    EPSILON = 0.95 # Exploration rate
    EPSILON_DECAY = 0.999 # Decay rate
    DISCOUNT = 0.90
    MIN_EPSILON = 0.01 # Minimum exploration rate
    UPDATE_TARGET_INTERVAL = 500

    env = CryptoEnvironment(df, lookback_window=LOOKBACK_WINDOW)
    state = env.reset()
    print(state.shape)
    agent = CryptoAgent(input_shape=state.shape)

    update_counter = 0
    rewardHistory = []

    for episode in range(200):
        episode_reward = 0
        step_count = 0

        state = env.reset()

        done = False

        while not done:
            env.render()

            r = random.randint(0, 2)

            if (r <= EPSILON):
               action = random.choice(ActionSpace)
            else:
                array_state = np.asarray(state)
                q_values = agent.predict_network_q(array_state.reshape(1,18))
                action = ActionSpace(np.argmax(q_values))

        new_state, reward, done, info = env.step(action)

        if done and step_count < 199:
            reward = -10

        step_count += 1

        step = (state, action, reward, new_state, done)
        agent.append_to_replay_memory(step)
        state = new_state
        episode_reward += reward

        # when enough steps in replay memory -> train network
        if len(agent.replay_memory) > BATCH_SIZE:
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
    rewardHistory.append(episode_reward)

    

if __name__ == '__main__':
    main()