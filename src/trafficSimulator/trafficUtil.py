import sys

from collections import defaultdict
from fixedRandom import FixedRandom


class Traffic(object):

    # time for the entire simulator
    globalTime = 0.0
    globalTimeLimit = sys.float_info.max

    SECOND_PER_HOUR = 3600.0

    carIsCrashed = False

    uniqueid = defaultdict(int)

    @classmethod
    def uniqueId(cls, idType):
        cls.uniqueid[idType] += 1
        return idType + "_" + str(cls.uniqueid[idType])

    @classmethod
    def updateGlobalTime(cls, deltaTime):
        if Traffic.globalTimeLimit - deltaTime < Traffic.globalTime:  # prevent overflow
            Traffic.globalTime = deltaTime - (Traffic.globalTimeLimit - Traffic.globalTime)
        else:
            Traffic.globalTime += deltaTime


class RoadType(object):
    ROAD = "Road"
    INTERSECTION = "Intersection"


class CarType(object):
    CAR = "car"
    TAXI = "taxi"


def sampleOne(list):
    """
    randomly pick one element from the given list.
    :param list:
    :return: a randomly picked item
    """
    return FixedRandom.sample(list, 1)[0]
