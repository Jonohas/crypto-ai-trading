# importing the tensorflow package
import tensorflow as tf
print(tf.__version__)
tf.test.is_built_with_cuda()
print(tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None))