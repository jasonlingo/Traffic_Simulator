from __future__ import division
import sys
from TrafficSettings import MAX_SPEED

class Lane(object):
    """
    A class that represents the lane of a road. A road might have more than one lane in one direction.
    """

    def __init__(self, road):
        """
        Construct a lane for the road
        :param road: the road that this lane belongs to
        """
        # TODO: move speed parameter to class Lane?
        self.road = road
        # self.leftAdjacent = None
        # self.rightAdjacent = None
        # self.leftmostAdjacent = None
        # self.rightmostAdjacent = None
        # self.length = haversine(self.source.center, self.target.center)
        # self.middleLine = None
        self.carsPosition = {}
        self.blocked = False

        # self.update()

    # def getSourceSideId(self):
    #     return self.road.sourceSideId
    #
    # def getTargetSideId(self):
    #     return self.road.targetSideId
    #
    # def getSideId(self):
    #     roads = self.road

    def getRoadId(self):
        return self.road.id

    # def isRightmost(self):
    #     return self == self.rightmostAdjacent
    #
    # def isLeftmost(self):
    #     return self == self.leftmostAdjacent

    def getSource(self):
        """Get source intersection"""
        return self.road.getSource()

    def getTarget(self):
        """Get target intersection"""
        return self.road.getTarget()

    def getLength(self):
        """Get the length of this lane (equals to the length of road)"""
        return self.road.getLength()

    # def getLeftBorder(self):
    #     return Segment(self.sourceSegment.source, self.targetSegment.target)
    #
    # def getRightBorder(self):
    #     return Segment(self.sourceSegment.target, self.targetSegment.source)

    # def update(self):
    #     self.middleLine = Segment(self.sourceSegment.center, self.targetSegment.center)
    #     self.length = self.middleLine.length
    #     self.direction = self.middleLine.direction

    def getTurnDirection(self, nextRoad):
        return self.road.getTurnDirection(nextRoad)

    # def getDirection(self):
    #     return self.direction

    def getPoint(self, a):
        """
        return the coordinates of the position on this lane according to the relative position "a".
        :param a: the relative position from 0(source) to 1(target)
        :return: (longitude, latitude)
        """
        lng = self.getSource().center.lng + (self.getTarget().center.lng - self.getSource().center.lng) * min(a, 1)
        lat = self.getSource().center.lat + (self.getTarget().center.lat - self.getSource().center.lat) * min(a, 1)
        return lng, lat

    def addCarPosition(self, carPos):
        """
        Add the given carPos (LanePosition) to the self.carsPosition dictionary
        :param carPos: (LanePosition)
        """
        if carPos.id in self.carsPosition:
            print "car is already here"
        else:
            self.carsPosition[carPos.id] = carPos

    def getCurAvgLaneSpeed(self):
        carsSpd = [pos.car.getSpeed() for pos in self.carsPosition.values()]
        if len(carsSpd) > 0:
            return sum(carsSpd) / len(carsSpd)
        else:
            return MAX_SPEED

    def removeCar(self, carPos):
        if carPos.id not in self.carsPosition:
            print "removing unknown car"
        del self.carsPosition[carPos.id]

    def getNext(self, carPos):
        """
        Find the car in front of the given parameter "carPos".
        :param carPos: a LanePosition of a car
        :return: the front car's LanePositions
        """
        if carPos.lane != self:
            print "car is on other lane"
            return []
        next = []
        shortestDist = sys.maxint
        for cp in self.carsPosition.itervalues():
            if cp.isGoalFlag:
                next.append(cp)
                continue
            if cp.position is None:
                print "the car has no position"
                continue
            if cp.car.id == carPos.car.id:
                continue
            distance = cp.position - carPos.position
            if not cp.free and (0 < distance < shortestDist):  # only pick the cars in front of current car
                shortestDist = distance
                next.append(cp)
        return next

    def getCars(self):
        return [cp.car for cp in self.carsPosition.values()]

    def isBlocked(self):
        return self.blocked

    def setBlocked(self, b):
        self.blocked = b

    def getAvgSpeed(self):
        if len(self.carsPosition) == 0:
            return sys.maxint
        return sum([lanePos.car.getSpeed() for lanePos in self.carsPosition.values()]) / len(self.carsPosition)

    def canSwitchLane(self, position, carLength):
        """
        Check there is enough room for the car on the neighbor lane to switch to this lane.
        :param position:
        :return: boolean
        """
        carPositions = [(c.position - c.car.length / 2, c.position + c.car.length / 2) for c in self.carsPosition.values()]
        for rear, front in carPositions:
            if rear <= position <= front:
                return False
        return True
