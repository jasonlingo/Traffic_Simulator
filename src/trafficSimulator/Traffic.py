import random
from math import radians, cos, sin, asin, sqrt, atan2, pi
from TrafficSettings import *
from collections import defaultdict


class Traffic(object):
    uniqueid = defaultdict(int)

    @classmethod
    def uniqueId(cls, idType):
        cls.uniqueid[idType] += 1
        return idType + "_" + str(cls.uniqueid[idType])


class RoadType(object):
    ROAD = "Road"
    INTERSECTION = "Intersection"


def sample(obj, n):
    """
    return a shuffled sub-list of objects
    :param obj: the given list
    :param n: the number of samples
    :return: a list of random samples
    """
    return shuffle(obj)[:max(0, n)]


def shuffle(obj):
    """
    Shuffle a given list and return a shuffled list.
    First create a copy of the original list in order
    to prevent that the original list will be affected
    by the shuffle operation.
    :param obj: the given list
    :return: a shuffled list
    """
    shuffled = obj[:]
    random.shuffle(shuffled)
    return shuffled


def rand(min, max):
    return random.choice([x for x in range(min, max+1)])

# def each(obj, iterator, context):
#     """
#
#     :param obj:
#     :param iterator:
#     :param context:
#     :return:
#     """
#     if obj is None:
#         return obj
#
#     if (nativeForEach && obj.forEach === nativeForEach):
#         obj.forEach(iterator, context)
#     else if (obj.length === +obj.length):
#         for (var i = 0, length = obj.length; i < length; i++) {
#            if (iterator.call(context, obj[i], i, obj) === breaker)
#             return
#     else:
#         for i in range(len(obj)):
#             if iterator.call(context, obj[keys[i]], keys[i], obj) == breaker:
#                 return
#     return obj

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

    # The radius of earth in kilometers.
    if METER_TYPE == "K":
        r = EARTH_RADIUS_KM    # The radius of earth in kilometers.
    else:
        r = EARTH_RADIUS_MILE  # The radius of earth in miles.
    return c * r


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