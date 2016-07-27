import math


class Point(object):

    def __init__(self, atX=0, atY=0):
        self.x = atX
        self.y = atY

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.Y)

    def direction(self):
        return math.atan2(self.y, self.x)

    def normalized(self):
        return Point(self.x / self.length(), self.y / self.length())

    def add(self, o):
        return Point(self.x + o.x, self.y + o.y)

    def subtract(self, o):
        return Point(self.x - o.x, self.y - o.y)

    def mult(self, k):
        return Point(self.x * k, self.y * k)

    def divide(self, k):
        return Point(self.x / float(k), self.y / float(k))