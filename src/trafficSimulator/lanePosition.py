from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from trafficUtil import Traffic


class LanePosition(object):
    """
    A class that represents the position of a car on a lane.
    """

    def __init__(self, car, lane=None, position=0):
        """
        :param car: Car object
        :param lane: Lane object, this lane that the given car is moving on
        :param position: The relative position (0~1) of this car on the lane
        """
        self.car = car
        self.lane = lane
        self.position = position
        self.id = Traffic.uniqueId("lanePosition")
        self.free = True  # True: this LanePosition is released; False: this LanePosition has been added to a lane
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

    def getCar(self):
        return self.car

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
        self.position = max(0, self.position + pos)  # no backward
        self.position = min(self.position, self.lane.getLength())

    def nextCarDistance(self):
        """
        Find the nearest car in front of this car and the distance.
        :return: the nearest car, distance (km)
        """
        # get the LanePosition in front of this car
        nextLanePosition = self.getNext()
        # calculate the head position of this car
        frontPosition = self.position + self.car.length / 2.0

        # find the nearest car in front of this car
        nextCar = None
        # nextRearPos = self.lane.getLength() if self.lane else sys.maxint
        nextRearPos = sys.maxint

        if nextLanePosition:
            rearPosition = nextLanePosition.position - (nextLanePosition.car.length / 2.0 if nextLanePosition.car else 0)
            if frontPosition <= rearPosition < nextRearPos:
                nextCar = nextLanePosition.car
                nextRearPos = rearPosition

        return nextCar, nextRearPos - frontPosition

    def acquire(self):
        """
        Add this LanePosition to the current lane.
        """
        if self.lane:
            self.free = False
            self.lane.addCarPosition(self)
            self.getRoad().addCarDriveTime(self.car.id, Traffic.globalTime, self.relativePosition())

    def release(self):
        """
        Remove this LanePosition from the current lane
        """
        if not self.free and self.lane:
            self.free = True
            self.lane.removeCar(self)
            self.getRoad().deleteCarDriveTime(self.car.id, Traffic.globalTime, self.relativePosition())

    def updateCarDriveTime(self):
        self.getRoad().updateCarDriveTime(self.car.id, self.relativePosition())

    def getNext(self):
        """
        Get the front car of this current car
        :return: a list that contains the front car's and the goal's LanePositions
        """
        if self.lane and not self.free:
            return self.lane.getNext(self)
        return None

