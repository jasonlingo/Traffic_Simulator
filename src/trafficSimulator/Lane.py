from __future__ import division
import sys
import math
from TrafficSettings import MAX_SPEED
from Coordinate import Coordinate

LANE_WIDTH = 0.0005  # latitude or longitude degree, it is about 5-meters long


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
        self.rightLane = None
        self.laneIdx = None

        # for shifting the coordinates to indicate the positions at different lanes.
        self.shiftSource = None
        self.shiftTarget = None

    # def getSourceSideId(self):
    #     return self.road.sourceSideId
    #
    # def getTargetSideId(self):
    #     return self.road.targetSideId
    #
    # def getSideId(self):
    #     roads = self.road

    def isRightLane(self):
        if self.rightLane is None:
            if self == self.road.getLanes()[-1]:
                self.rightLane = True
        return self.rightLane

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
        if self.shiftSource is None or self.shiftTarget is None:
            self.updateShift()

        a = min(a, 1)
        lng = self.shiftSource.lng + (self.shiftTarget.lng - self.shiftSource.lng) * a
        lat = self.shiftSource.lat + (self.shiftTarget.lat - self.shiftSource.lat) * a
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

    # def isCarPositionEmpty(self, pos):            # TODO: check position is empty
    #     for pos in self.carsPosition.values():
    #         if

    def getFrontAvgSpeed(self, pos):
        """
        Get the average speed of cars in front of the given position.
        :param pos: absolute position
        :return: the average speed in front of the given position
        """
        frontCarSpeed = [cp.getCar().getSpeed() for cp in self.carsPosition.values()
                                                if cp.getPosition() - cp.getCar().length / 2 > pos]
        if not frontCarSpeed:
            return sys.maxint
        return sum(frontCarSpeed) / len(frontCarSpeed)

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

    def canSwitchLane(self, position):
        """
        Check there is enough room for the car on the neighbor lane to switch to this lane.
        :param position:
        :return: boolean
        """
        carPositions = [(c.position - c.car.length / 2, c.position + c.car.length / 2)
                        for c in self.carsPosition.values()]
        for rear, front in carPositions:
            if rear <= position <= front:
                return False
        return True

    def updateShift(self):
        """
        Update the new source and target coordinates.
        First, we find the perpendicular vector to the vector of this lane. Two vectors are
        perpendicular if the product of the vector is 0.
        """
        if self.shiftSource is None and self.shiftTarget is not None:
            return

        # shift unit is the multiplier for the shift distance
        # the left-most lane will shift 0.5 * LANE_WIDTH,
        # the second left-most lane will shift 1.5 * LANE_WIDTH, and so on
        shiftUnit = self.laneIndex() + 0.5
        shiftDist = LANE_WIDTH * shiftUnit

        source = self.road.getSource().getCoords()  # lng, lat
        target = self.road.getTarget().getCoords()  # lng, lat
        vector = target[0] - source[0], target[1] - source[1]
        if vector[0] == 0:  # vertical lane
            self.shiftSource = Coordinate(source[0], source[1] + shiftDist)
            self.shiftTarget = Coordinate(target[0], target[1] + shiftDist)
        elif vector[1] == 0:  # horizontal lane
            self.shiftSource = Coordinate(source[0] + shiftDist, source[1])
            self.shiftTarget = Coordinate(target[0] + shiftDist, target[1])
        else:
            lngShift, latShift = Lane.shiftUnit(vector, shiftDist)
            self.shiftSource = Coordinate(source[0] + lngShift, source[1] + latShift)
            self.shiftTarget = Coordinate(target[0] + lngShift, target[1] + latShift)

    def laneIndex(self):
        if self.laneIdx is None:
            lanes = self.road.getLanes()
            for i, lane in enumerate(lanes):
                if lane == self:
                    self.laneIdx = i
                    break
        return self.laneIdx

    @classmethod
    def shiftUnit(cls, vector, dist):
        """
        Calculate the shift unit for the lng and lat coordinates so that we
        can get a parallel line with a distance between these two lines.

        :param vector: the vector of the original line
        :param dist: the distance between the wo parallel lines
        :return: the unit vector for the perpendicular line
        """
        # two vectors: v1, v2; v1[0] is x vector, v1[1] is y vector
        # v1[0] * v2[0] + v1[1] * v2[1] = 0, then v1 is perpendicular to v2
        # v2[0] / v2[1] = -v1[1] / v1[0]
        lngLatRatio = -vector[1] / vector[0]

        # since we want to add a perpendicular line, we have the equation:
        # lng = lngLatRatio * lat and lng^2 + lat^2 == dist^2
        # lngLatRatio^2 * lat^2 + lat^2 = dist^2
        # lat = sqrt(dist^2 / (1 + lngLatRatio^2)) = dist * sqrt(1 + lngLatRatio^2)
        lat = dist / math.sqrt(1 + lngLatRatio * lngLatRatio)  # currently lat must be a positive value

        # if the value of the original vector are of the same sign,
        # then the lat value is of the opposite sign
        if vector[0] * vector[1] > 0:  # lat's sign must be opposite to vector[1]
            if vector[1] > 0:
                lat *= -1
        else:                          # lat's sign must be the same with vector[1]
            if vector[1] < 0:
                lat *= -1

        return lat * lngLatRatio, lat


# vector = (1, 2)
# lng, lat = Lane.shiftUnit(vector, 1)
# print lng, lat
# print lng * lng + lat * lat