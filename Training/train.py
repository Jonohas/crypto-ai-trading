# get values from environment variables

# Path: Training/train.py

import pandas as pd
import numpy as np
import os
import sys
from dotenv import load_dotenv
from tqdm import tqdm
import random
import time

from CryptoEnvironment import CryptoEnvironment
from CryptoAgent import CryptoAgent
from ActionSpace import ActionSpace

load_dotenv()

class Train():
    def __init__(self, data_path):
        self._data = pd.read_csv(data_path)

        self.root_dir = os.path.join('../', 'Results', 'progress')
        # cut off random amount of rows from the first half
        self._data = self._data.iloc[random.randint(0, int(self._data.shape[0] / 2)):]
        self._training_data = self._data.drop(['original_open', 'original_close', 'original_high', 'original_low', 'original_volume', 'event_time'], axis=1)
        
        self._create_log_dir()
        self.env_risk = float(os.getenv("ENVIRONMENT_RISK_FACTOR"))
        self.env_initial_balance = float(os.getenv("ENVIRONMENT_INITIAL_BALANCE"))
        self.env_initial_coin_amount = float(os.getenv("ENVIRONMENT_INITIAL_COIN_AMOUNT"))
        self.env_sequence_length = int(os.getenv("ENVIRONMENT_SEQUENCE_LENGTH"))
        self.env_look_back_window = int(os.getenv("ENVIRONMENT_LOOK_BACK_WINDOW"))
        self.env_look_ahead_window = int(os.getenv("ENVIRONMENT_LOOK_AHEAD_WINDOW"))
        self.env_profitable_sell_threshhold = float(os.getenv("ENVIRONMENT_PROFITABLE_SELL_THRESHHOLD"))
        self.env_profitable_sell_reward = float(os.getenv("ENVIRONMENT_PROFITABLE_SELL_REWARD"))

        self.batch_size = int(os.getenv("BATCH_SIZE"))
        self.epochs = int(os.getenv("EPOCHS"))
        self.learning_rate = float(os.getenv("LEARNING_RATE"))
        self.discount = float(os.getenv("DISCOUNT"))
        self.epsilon = float(os.getenv("EPSILON"))
        self.epsilon_decay = float(os.getenv("EPSILON_DECAY"))
        self.epsilon_decay_start = int(os.getenv("EPSILON_DECAY_START"))
        self.min_epsilon = float(os.getenv("MIN_EPSILON"))
        self.update_target_interval = int(os.getenv("UPDATE_TARGET_INTERVAL"))
        self.save_model_interval = int(os.getenv("SAVE_MODEL_INTERVAL"))
        self.fee = float(os.getenv("ENVIRONMENT_FEE"))

        self.step_limit = int(os.getenv("STEP_LIMIT"))

        self.replay_buffer_capacity = int(os.getenv("REPLAY_BUFFER_CAPACITY"))

        self._verbose = bool(os.getenv("VERBOSE"))

        self.input_shape = (self.env_sequence_length, self._data.shape[1] + 2)
        self.training_input_shape = (self.env_sequence_length, self._training_data.shape[1] + 2)

        self._use_previous_model = bool(os.getenv("USE_PREVIOUS_MODEL"))
        self._previous_model_path = os.getenv("LOAD_MODEL_PATH")
        self._previous_model_index = os.getenv("LOAD_MODEL_INDEX")

        self.env_consecutive_threshold = int(os.getenv("ENVIRONMENT_CONSECUTIVE_THRESHOLD"))

        model_arguments = {
            'previous_model_path': self._previous_model_path,
            'previous_model_index': self._previous_model_index,
            'use_previous_model': self._use_previous_model,
            'learning_rate': self.learning_rate,
        }

        arguments={
            'risk':  self.env_risk,
            'initial_balance':  self.env_initial_balance,
            'initial_coin_amount':  self.env_initial_coin_amount,
            'sequence_length':  self.env_sequence_length,
            'look_back_window':  self.env_look_back_window,
            'look_ahead_window':  self.env_look_ahead_window,
            'profitable_sell_threshhold':  self.env_profitable_sell_threshhold,
            'profitable_sell_reward':  self.env_profitable_sell_reward,
            'step_limit': self.step_limit,
            'consecutive_threshold': self.env_consecutive_threshold,
            'fee': self.fee,
        }

        self._env = CryptoEnvironment(self._data, self._training_data, arguments, self.input_shape, self.log_dir, verbose=self._verbose, render=True)
        self._agent = CryptoAgent(self.replay_buffer_capacity, self.training_input_shape ,self.root_dir,  self.log_dir, model_arguments, verbose=self._verbose)

        self.write_to_log(self.log_dir + "/reward_history.csv", ['episode', 'reward', 'average_reward', 'epsilon', 'step_count', 'profit'])
        

    def write_to_log(self, path, items):
        i = 0
        with open(path, "a+") as f:
            for item in items:
                if i != 0:
                    f.write(",")
                f.write(f"{item}")
                i += 1

            f.write("\n")

    def _create_log_dir(self):
        log_dir = os.getenv("SAVE_PATH")

        timestamp = time.time()
        string_time = time.strftime("%Y-%m-%d_%H%M%S", time.localtime(timestamp))
        log_dir = os.path.join(log_dir, str(string_time))
            

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not os.path.exists(log_dir + "/episodes"):
            os.makedirs(log_dir + "/episodes")

        if not os.path.exists(log_dir + "/models"):
            os.makedirs(log_dir + "/models")

        if not os.path.exists(log_dir + "/images"):
            os.makedirs(log_dir + "/images")

        self.log_dir = log_dir


    def train(self):
        update_counter = 0
        reward_history = []
        average_reward_history = []
        average_reward = 0

        progress_bar = tqdm(range(self.epochs), desc="Episodes", unit="episodes")

        for episode in progress_bar:
            episode_string = str(episode)
            if episode < 10:
                episode_string = "0" + episode_string
            if episode < 100:
                episode_string = "0" + episode_string

            episode_history_path = self.log_dir + f"/episodes/{episode_string}_episode_history.csv"

            self.write_to_log(episode_history_path, ["step", "reward", "profit", "balance", "coin_amount", "action", "random"])
            episode_reward = 0
            step_count = 0
            done = False

            state = self._env.reset()

            while not done:
                r = random.random()
                progress_bar.set_description(f"Episode: {episode}, Step: {step_count}, Epsilon: {self.epsilon}")

                is_random_action = False

                if r <= self.epsilon:
                    action = self._env.random_action()
                    is_random_action = True

                else:
                    data_for_nn = self._env._get_sequence(self._env._tick)
                    array_state = np.asarray(data_for_nn)
                    feature_count = array_state.shape[1]
                    q_values = self._agent.predict_q(array_state.reshape(1, self.env_sequence_length, feature_count), 1)
                    action = ActionSpace(np.argmax(q_values))


                next_state, reward, done, info = self._env.step(action.value, is_random_action)
                

                training_state = self._env._get_sequence(self._env._tick)
                training_next_state = self._env._get_sequence(self._env._tick + 1)
                step = (training_state, action.value, reward, training_next_state, done)

                self._agent.add_to_memory(step)
                state = next_state
                episode_reward += reward

                self.write_to_log(episode_history_path, [step_count, reward, info["profit"], info["account_balance"], info["coin_amount"], action.value, is_random_action])
                step_count += 1

            reward_history.append(episode_reward)
            average_reward = np.mean(reward_history)

            if len(self._agent.memory) > self.batch_size:
                if self.epsilon_decay_start <= episode:
                    self.epsilon = self.epsilon_decay * self.epsilon
                    if self.epsilon < self.min_epsilon:
                        self.epsilon = self.min_epsilon

                minibatch_samples = self._agent.sample_memory(self.batch_size)

                mini_batch = []

                for item in minibatch_samples:
                    mini_batch.append((item[0], item[1], item[2], item[3], item[4]))

                mini_batch_states = np.asarray(list(zip(*mini_batch))[0],dtype=float)
                mini_batch_actions = np.asarray(list(zip(*mini_batch))[1], dtype=int)
                mini_batch_rewards = np.asarray(list(zip(*mini_batch))[2],dtype=float)
                mini_batch_next_states = np.asarray(list(zip(*mini_batch))[3],dtype=float)
                mini_batch_done = np.asarray(list(zip(*mini_batch))[4],dtype=bool)

                current_state_q_values = self._agent.predict_q(mini_batch_states, batch_size=self.batch_size)
                y = current_state_q_values

                next_state_q_values = self._agent.predict_target(mini_batch_next_states, batch_size=self.batch_size)

                max_q_next_state = np.max(next_state_q_values, axis=1)

                for i in range(self.batch_size):
                    if mini_batch_done[i]:
                        y[i, mini_batch_actions[i]] = mini_batch_rewards[i]
                    else:
                        y[i, mini_batch_actions[i]] = mini_batch_rewards[i] + self.discount * max_q_next_state[i]

                self._agent.fit_q(mini_batch_states, y, batch_size=self.batch_size)

            else:
                continue
            if update_counter == self.update_target_interval:
                self._agent.update_target()
                update_counter = 0
            update_counter += 1
            
            reward_history.append(episode_reward)
            self._env.render(episode)
            


            if episode % self.save_model_interval == 0:
                self._agent.save_model(episode)

            self.write_to_log(self.log_dir + "/reward_history.csv", [episode, episode_reward / step_count, average_reward, self.epsilon, step_count, self._env._total_profit])
            

        self._agent.save_model('final')



if __name__ == "__main__":
    data_path = os.getenv("DATA_PATH")
    train = Train(data_path)
    train.train()
