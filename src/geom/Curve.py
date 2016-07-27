from Segment import Segment


class Curve(object):
    """
    A class that deals with the car's turning curve.
    """

    def __init__(self, atA, atB, atO, atQ):
        self.a = atA
        self.b = atB
        self.o = atO
        self.q = atQ
        self.ab = Segment(self.a, self.b)
        self.ao = Segment(self.a, self.o)
        self.oq = Segment(self.o, self.q)
        self.qb = Segment(self.q, self.b)
        self.length = None

    def length(self):
        if not self.length:
            pointsNumber = 10
            prevoiusPoint = None
            self.length = 0
            for i in range(pointsNumber):
                point = self.getPoint(i / float(pointsNumber))
                if prevoiusPoint:
                    self.length += point.subtract(prevoiusPoint).length
                prevoiusPoint = point
        return self.length

    def getPoint(self, a):
        p0 = self.ao.getPoint(a)
        p1 = self.oq.getPoint(a)
        p2 = self.qb.getPoint(a)
        r0 = Segment(p0, p1).getPoint(a)
        r1 = Segment(p1, p2).getPoint(a)
        return Segment(r0, r1).getPoint(a)

    def getDirection(self, a):
        p0 = self.ao.getPoint(a)
        p1 = self.oq.getPoint(a)
        p2 = self.qb.getPoint(a)
        r0 = Segment(p0, p1).getPoint(a)
        r1 = Segment(p1, p2).getPoint(a)
        return Segment(r0, r1).direction



