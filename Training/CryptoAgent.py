from collections import deque
from CryptoModel import CryptoModel
import random



import tensorflow as tf
# set memory growth to true
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


class CryptoAgent:
    def __init__(self, replay_buffer_capacity, input_shape, log_dir, verbose=False):
        self.capacity = replay_buffer_capacity
        self.memory = deque(maxlen=self.capacity)
        self.populated = False
        self.log_dir = log_dir

        self._input_shape = input_shape

        self._verbose = verbose

        self._model_q = CryptoModel(self._input_shape, self.log_dir)
        self._model_target = CryptoModel(self._input_shape, self.log_dir)

    def sample_memory(self, batch_size):
        if batch_size > len(self.memory):
            self.populated = False
            return self.populated
        else:
            return random.sample(self.memory, batch_size)

    def add_to_memory(self, step):
        self.memory.append(step)

    def fit_q(self, X, y, batch_size):
        self._model_q.train(X, y, batch_size)
    
    def predict_q(self, sequence, batch_size):
        return self._model_q.predict(sequence, batch_size)

    def predict_target(self, sequence, batch_size):
        return self._model_target.predict(sequence, batch_size)

    def update_target(self):
        self._model_target.update(self._model_q.get_weights())

    def save_model(self, index):
        self._model_target.save_model(index)
