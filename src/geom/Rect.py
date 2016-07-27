from Point import Point
from Segment import Segment
import math


class Rect(object):

    def __init__(self, x, y, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def copy(self, rect):
        return Rect(rect.x, rect.y, rect.width, rect.height)

    def area(self):
        return self.width * self.height

    # def left(self, left):
    #     if left:
    #         self.x = left
    #     return self.x
    #
    # def right(self, right):
    #     if right:
    #         self.x = right - self.width
    #     return self.x + self.width
    #
    # def width(self, width):
    #     if width:
    #         self.width = width
    #     return self.width
    #
    # def top(self, top):
    #     if top:
    #         self.y = top
    #     return self.y
    #
    # def bottom(self, bottom):
    #     if bottom:
    #         self.y = bottom - self.height
    #     return self.y + self.height
    #
    # def height(self, height):
    #     if height:
    #         self.height = height
    #     return self.height
    #
    def center(self):
        # if center:
        #     self.x = center.x - self.width / 2.0
        #     self.y = center.y - self.height / 2.0
        return Point(self.x + self.width / 2.0, self.y + self.height / 2.0)
    #
    # def containsPoint(self, point):
    #     return self.left() <= point.x <= self.right() and \
    #            self.top() <= point.y <= self.bottom()
    #
    # def containsRect(self, rect):
    #     return self.left() <= rect.left() <= self.right() and \
    #            self.top() <= rect.top() and \
    #            rect.bottom() <= self.bottom()

    # def getVertices(self):
    #     topLeft = Point(self.left(), self.top())
    #     topRight = Point(self.right(), self.top())
    #     rightBot = Point(self.right(), self.bottom())
    #     leftBot = Point(self.left(), self.bottom())
    #     return [topLeft, topRight, rightBot, leftBot]

    def getSide(self, i):
        vertices = self.getVertices()
        return Segment(vertices[i], vertices[(i + 1) % 4])

    def getSectorId(self, point):
        offset = point.subtract(self.center())
        if offset.y <= 0 and abs(offset.x) <= abs(offset.y):
            return 0
        if offset.x >= 0 and abs(offset.x) >= abs(offset.y):
            return 1
        if offset.y >= 0 and abs(offset.x) <= abs(offset.y):
            return 2
        if offset.x <= 0 and abs(offset.x) >= abs(offset.y):
            return 3
        print "algorithm error"

    def getSector(self, point):
        return self.getSide(self.getSectorId(point))


