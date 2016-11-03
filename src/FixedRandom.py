import random
import numpy as np


class FixedRandom(object):
    """
    Fix the random seed so that the randomness can be fixed for every experiment.
    """

    SEED = 0
    rand = random.Random(SEED)  # fix the random seed
    np.random.seed(SEED)

    @classmethod
    def random(cls):
        return cls.rand.random()

    @classmethod
    def sample(cls, population, k):
        return cls.rand.sample(population, k)

    @classmethod
    def choice(cls, seq):
        return cls.rand.choice(seq)

    @classmethod
    def randint(cls, a, b):
        return cls.rand.randint(a, b)

    @classmethod
    def poisson(cls, lam, size=None):
        return np.random.poisson(lam, size)
