from math import atan2, degrees
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_xlim(-0.05, 1)
# ax.set_ylim(-0.05, 1)
# plt.grid('on')

# Rotate rectangle patch object
# ts = ax.transData
# coords = ts.transform([0.4, 0.6])
# tr = mpl.transforms.Affine2D().rotate_deg_around(coords[0], coords[1], 170)
# t = ts + tr
#
# rec0 = patches.Rectangle((0.2, 0.5), 0.4, 0.2, alpha=0.5)
# ax.add_patch(rec0)
#
# #Rotated rectangle patch
# rect1 = patches.Rectangle((0.2, 0.5), 0.4, 0.2, color='blue', alpha=0.5, transform=t)
# ax.add_patch(rect1)

#The (desired) point of rotation
# ax.scatter([0.0,0.2],[0.0,0.5], c=['g','r'],zorder=10)
# txt = ax.annotate('Desired point of rotation',xy=(0.2,0.5),fontsize=16,\
# xytext=(0.25,0.35),arrowprops=dict(arrowstyle="->",connectionstyle="arc3,rad=-.2"))
# txt2 = ax.annotate('Actual point of rotation',xy=(0.0,0.0),fontsize=16,\
# xytext=(0.15,0.15),arrowprops=dict(arrowstyle="->",connectionstyle="arc3,rad=.2"))

# plt.show()

def getRectangle(ax, center, width, height, head, color):
    """
    Make a rotated rectangle according to the given center and the degree between
    the center and the head.

    :param ax: matplotlib ax object
    :param center: (float, float) the longitude and latitude for the center.
    :param width: (float)
    :param height: (float)
    :param head: (float, float) the longitude and latitude for calculating the rotated degree.
    :param color: (str) the color for this rectangle
    :return: a rectangle
    """
    # calculate the left-bottom of the rectangle.
    orgLng = int(center[0] - width / 2.0)
    orgLat = int(center[1] - height / 2.0)

    # calculate the degree
    deg = getDegree(center, head)

    # calculate the rotation
    ts = ax.transData
    coords = ts.transform([center[0], center[1]])
    tr = mpl.transforms.Affine2D().rotate_deg_around(coords[0], coords[1], deg)
    t = ts + tr

    rect = patches.Rectangle((orgLng, orgLat), width, height, color=color, alpha=0.9, transform=t)

    return rect


def getDegree(ptr1, ptr2):
    """
    Calculate the degree of the vector p1 -> p2.
    :param ptr1:
    :param ptr2:
    :return:
    """
    dx = ptr2[0] - ptr1[0]
    dy = ptr2[1] - ptr1[1]
    rads = atan2(dy, dx)
    return degrees(rads)

