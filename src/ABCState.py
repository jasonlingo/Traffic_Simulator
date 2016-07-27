from abc import ABCMeta, abstractmethod


class ABC_State(object):
    """
    An abstract class for state.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def getState(self):
        raise NotImplementedError()
