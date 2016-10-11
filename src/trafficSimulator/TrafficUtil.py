import sys
import random
from collections import defaultdict
from math import radians, cos, sin, asin, sqrt, atan2, pi

from Coordinate import Coordinate
from src.trafficSimulator.config import *


class Traffic(object):

    # time for the entire simulator
    globalTime = 0.0
    globalTimeLimit = sys.float_info.max

    uniqueid = defaultdict(int)

    @classmethod
    def uniqueId(cls, idType):
        cls.uniqueid[idType] += 1
        return idType + "_" + str(cls.uniqueid[idType])

class RoadType(object):
    ROAD = "Road"
    INTERSECTION = "Intersection"

class CarType(object):
    CAR = "car"
    TAXI = "taxi"

class DistanceUnit(object):
    KM = "KM"
    MILE = "MILE"

    # The radius of the earth in kilometers
    EARTH_RADIUS_KM = 6371.0

    # The radius of the earth in miles
    EARTH_RADIUS_MILE = 3959.0

def sampleOne(list):
    """
    randomly pick one element from the given list.
    :param list:
    :return: a randomly picked item
    """
    return random.sample(list, 1)[0]


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Args:
      (tuple) poitn1: the position of the first point
      (tuple) point2: the position of the second point
    Return:
      (float) distance (in km) between two nodes
    """
    # Convert decimal degrees to radians
    lng1, lat1 = point1.getCoords()
    lng2, lat2 = point2.getCoords()
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))

    # The radius of earth in kilometers or miles.
    if METER_TYPE == DistanceUnit.KM:
        r = DistanceUnit.EARTH_RADIUS_KM    # The radius of earth in kilometers.
    else:
        r = DistanceUnit.EARTH_RADIUS_MILE  # The radius of earth in miles.
    return c * r


# calculate the approximate GPS distance unit
p1 = Coordinate(0.0, 1.0)
p2 = Coordinate(0.0, 0.0)
GPS_DIST_UNIT = haversine(p1, p2)


def distToGPSDiff(length):
    """
    Invert length in kilometer to GPS unit. Use the haversine function.
    :param km:
    :return:
    """
    # The radius of earth in kilometers or miles.
    # if METER_TYPE == "K":
    #     r = EARTH_RADIUS_KM  # The radius of earth in kilometers.
    # else:
    #     r = EARTH_RADIUS_MILE  # The radius of earth in miles.
    #
    # c = km / r
    # a = pow(sin(c / 2.0), 2)
    # dlng = asin(a / 2.0)
    #
    # lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    return length / GPS_DIST_UNIT


def calcVectAngle(vec1, vec2):
    """
    Calculate the clock-wise angle between two vectors.
    :param vec1: (float, float) the first vector that is used as the starting point for
                 the angle.
    :param vec2: (float, float) the second vector
    """
    angle = atan2(vec1[0], vec1[1]) - atan2(vec2[0], vec2[1])
    angle = angle * 360 / (2 * pi)
    if angle < 0:
        angle += 360
    return angle