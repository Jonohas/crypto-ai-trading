import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}


import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  for gpu in gpus:
    print(gpu)
    tf.config.experimental.set_memory_growth(gpu, True)
else:
  print("No GPU device found")
print(tf.__version__)
