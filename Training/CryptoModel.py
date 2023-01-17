import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import gc

class CryptoModel:
    def __init__(self, input_shape, root ,log_dir, model_arguments):
        self._verbose = False
        self.log_dir = log_dir
        self.input_shape = input_shape
        self._root = root

        self._model_arguments = model_arguments

        if self._model_arguments != {} and self._model_arguments['use_previous_model']:
            try:
                self.load_model(self._model_arguments['previous_model_path'], self._model_arguments['previous_model_index'])
            except:
                self.model = self._create_model()
        else:
            self.model = self._create_model()


    def _create_model(self):
        model = keras.Sequential()

        optimizer = Adam()

        model.add(layers.LSTM(200, input_shape=self.input_shape, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(128, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(64, return_sequences=True))
        model.add(layers.Dropout(0.2))
        model.add(layers.LSTM(32))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(16, activation='relu'))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(3, activation='softmax'))

        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['mae', 'accuracy'])
        return model

    def save_model(self, index):
        log_dir = self.log_dir + '/models/'
 
        self.model.save(log_dir + f'/model_{index}.h5')

    def load_model(self, path, index):
        dir = os.path.join(self._root, path)

        log_dir = dir + '/models/'
        self.model = keras.models.load_model(log_dir + f'model_{index}.h5')

    def train(self, X, y, batch_size):
        self.model.fit(X, y, batch_size=batch_size, verbose=self._verbose)

    def predict(self, sequence, batch_size):
        value = tf.convert_to_tensor(sequence, dtype=tf.float16)
        policy = self.model.predict(value, verbose=self._verbose, batch_size=batch_size)
        gc.collect()
        keras.backend.clear_session()
        return policy

    def update(self, weights):
        self.model.set_weights(weights)

    def get_weights(self):
        return self.model.get_weights()