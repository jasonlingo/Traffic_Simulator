from road import *
from intersection import *


class RoadFactory(object):
    """
    A class that makes road and intersections. This is a factory design pattern.
    """

    @classmethod
    def makeRoads(cls, roadType, corners, center):
        """
        Create a road or intersection according to the given road type.
        :param roadType: indicate a road or an intersection to be created
        :param corners: the corner coordinates of this road or intersection
        :param center: the center coordinates of this road or intersection
        :return: a created road or intersection
        """
        if roadType == RoadType.ROAD:
            return Road(corners, center, None, None)
        elif roadType == RoadType.INTERSECTION:
            return Intersection(corners, center, None)
