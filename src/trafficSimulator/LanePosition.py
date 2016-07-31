from __future__ import division
from Traffic import *
import sys


class LanePosition(object):
    """
    A class that represents the position of a car on a lane.
    """

    def __init__(self, car, lane=None, position=0):
        self.car = car
        self.lane = lane
        self.position = position
        self.id = Traffic.uniqueId("laneposition")
        self.free = True
        self.isGoalFlag = False

    def setGoal(self):
        self.isGoalFlag = True

    def isGoal(self):
        return self.isGoalFlag

    def getLane(self):
        return self.lane

    def setLane(self, lane):
        self.lane = lane

    def getRoad(self):
        return self.lane.road

    def getNextInter(self):
        return self.lane.road.getTarget()

    def relativePosition(self):
        return self.position / self.lane.getLength()

    def getPosition(self):
        """ return current position (km) from source intersection """
        return self.position

    def setPosition(self, pos):
        self.position = pos

    def addPosition(self, pos):
        self.position = max(0, self.position + pos)
        self.position = min(self.position, self.lane.getLength())

    def nextCarDistance(self):
        """
        Find the nearest car in front of this car and the distance.
        :return: the nearest car, distance (km)
        """
        # get a list of LanePosition in front of this car
        nextLanePossitions = self.getNext()
        # calculate the front position of this car
        frontPosition = self.position + self.car.length / 2.0

        # find the nearest car in front of this car
        nextCar = None
        # nextRearPos = self.lane.getLength() if self.lane else sys.maxint
        nextRearPos = sys.maxint
        for lanePosition in nextLanePossitions:
            # if lanePosition.isGoal() and not self.car.isTaxi: # FIXME: check if still need this
            #     continue
            rearPosition = lanePosition.position - (lanePosition.car.length / 2.0 if lanePosition.car else 0)
            if frontPosition <= rearPosition < nextRearPos:
                nextRearPos = rearPosition

        return nextCar, nextRearPos - frontPosition

    def acquire(self):
        """
        Add this LanePosition to the current lane
        """
        if self.lane:
            self.free = False
            self.lane.addCarPosition(self)

    def release(self):
        """
        Remove this LanePosition from the current lane
        """
        if not self.free and self.lane:
            self.free = True
            self.lane.removeCar(self)

    def getNext(self):
        """
        Get the front car of this current car
        :return: a list that contains the front car's and the goal's LanePositions
        """
        if self.lane and not self.free:
            return self.lane.getNext(self)
        return []

