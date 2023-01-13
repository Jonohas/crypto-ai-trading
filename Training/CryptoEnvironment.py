import gym

from ActionSpace import ActionSpace

class CryptoEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, data, verbose=False):
        super(CryptoEnvironment, self).__init__()
        pass

    def reset(self):
        pass

    def step(self, action):
        pass

    def render(self):
        pass

    def close(self):
        pass