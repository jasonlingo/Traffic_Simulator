from Traffic import *
from ControlSignals import ControlSignals


class Intersection(object):
    """
    A class that represents an intersection. It will have a traffic signal control
    to manage when cars can pass through the intersection.
    """

    def __init__(self, corners, center, rect):
        """
        :param corners: the four corners of this intersection
        :param center: the coordinate of the center of this intersection
        :param rect: the area of this intersection
        :return:
        """
        self.corners = corners
        self.center = center
        self.rect = rect
        self.id = Traffic.uniqueId(RoadType.INTERSECTION)
        self.outRoads = []
        self.inRoads = []
        self.controlSignals = ControlSignals(self)

    def update(self):
        for rd in self.outRoads:
            rd.update()
        result = []
        for ird in self.inRoads:
            result.append(ird.update())
        return result

    def getId(self):
        return self.id

    def getOutRoads(self):
        return self.outRoads

    def getInRoads(self):
        return self.inRoads

    def addOutRoad(self, rd):
        if rd.target.center.getCoords() not in [road.target.center.getCoords() for road in self.outRoads]:
            self.outRoads.append(rd)
        # else:
        #     print "duplicated out road"

    def addInRoad(self, rd):
        if rd.source.center.getCoords() not in [road.source.center.getCoords() for road in self.inRoads]:
            self.inRoads.append(rd)
        # else:
        #     print "duplicated in road"

    def buildControlSignal(self):
        self.controlSignals.generateState()

    # def getTurnDirection(self, lane):
    #     return self.controlSignals.getTurnDirection(lane)