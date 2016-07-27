from Road import *
from Intersection import *


class Factory(object):
    """
    A class that makes road and intersections. This is a factory design pattern.
    """


    @classmethod
    def makeRoads(cls, roadType, corners, center):
        """
        Create a road or intersection according to the given road type.
        :return: a created road or intersection
        """
        if roadType == RoadType.ROAD:
            return Road(corners, center, None, None)
        elif roadType == RoadType.INTERSECTION:
            return Intersection(corners, center)
