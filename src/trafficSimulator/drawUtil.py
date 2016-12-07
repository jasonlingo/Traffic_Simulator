from __future__ import division
from math import atan2
from math import degrees
from math import radians
from math import cos
from math import sin
from math import asin
from math import sqrt
import matplotlib as mpl

from coordinate import Coordinate
from config import METER_TYPE


class DistanceUnit(object):
    KM = "KM"
    MILE = "MILE"

    # The radius of the earth in kilometers
    EARTH_RADIUS_KM = 6371.0

    # The radius of the earth in miles
    EARTH_RADIUS_MILE = 3959.0


def setRectangle(ax, patch, center, width, height, head, flipCoord):
    """
    Make a rotated rectangle according to the given center and the degree between
    the center and the head.

    :param ax: matplotlib ax object
    :param patch: the rectangle patch object
    :param center: (float, float) the longitude and latitude for the center.
    :param width: (float)
    :param height: (float)
    :param head: (float, float) the longitude and latitude for calculating the rotated degree.
    :param color: (str) the color for this rectangle
    :param flipCoord: (boolean) True to change the GPS coordination system to pixel coordination system.
    :return: a rectangle
    """
    # calculate the degree
    deg = getDegree(center, head, flipCoord)

    # calculate the rotation
    ts = ax.transData
    coords = ts.transform([center[0], center[1]])
    tr = mpl.transforms.Affine2D().rotate_deg_around(coords[0], coords[1], deg)
    transform = ts + tr

    # set properties
    orgLng = center[0] - width / 2
    orgLat = center[1] - height / 2
    patch.set_x(orgLng)
    patch.set_y(orgLat)
    patch.set_width(width)
    patch.set_height(height)
    patch.set_transform(transform)


def getDegree(ptr1, ptr2, flipCoord):
    """
    Calculate the degree of the vector p1 -> p2.

    The GPS coordination system
     ^
     |
     |
     |________>
    0

    The pixel coordination system

    0 ________>
     |
     |
     |

    :param ptr1: (longitude, latitude)
    :param ptr2: (longitude, latitude)
    :param flipCoord: (boolean) True to change the GPS coordination system to pixel coordination system.
    :return:
    """
    dx = ptr2[0] - ptr1[0]
    if flipCoord:
        dy = ptr1[1] - ptr2[1]
    else:
        dy = ptr2[1] - ptr1[1]
    rads = atan2(dy, dx)
    return degrees(rads)


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


def distToGPSDiff(length):
    """
    Invert length in kilometer to GPS unit. Use the haversine function.
    :param km:
    :return:
    """
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


# calculate the approximate GPS distance unit
p1 = Coordinate(0.0, 1.0)
p2 = Coordinate(0.0, 0.0)
GPS_DIST_UNIT = haversine(p1, p2)
print "GPS_DIST_UNIT:", GPS_DIST_UNIT