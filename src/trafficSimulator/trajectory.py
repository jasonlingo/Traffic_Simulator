from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lanePosition import LanePosition


class Trajectory(object):
    """
    A class that represents the trajectory of a car.
    """

    def __init__(self, car, lane, position=0):
        """
        :param car:
        :param lane:
        :param position: the distance from the source to the car's locaiton
        :return:
        """
        self.car = car
        self.current = LanePosition(self.car, lane, position)
        self.current.acquire()
        self.next = LanePosition(self.car)
        self.isChangingLanes = False
        self.absolutePosition = None

    def setGoal(self):
        self.current.setGoal()

    def isGoal(self):
        return self.current.isGoal()

    def getLane(self):
        return self.current.lane

    def getRoad(self):
        return self.current.lane.road

    def getOppositeRoad(self):
        source = self.current.lane.road.getSource()
        sourceCoords = source.center.getCoords()
        target = self.current.lane.road.getTarget()
        for road in target.getOutRoads():
            if road.target.center.getCoords() == sourceCoords:
                return road

    def getAbsolutePosition(self):
        return self.current.position

    def getRelativePosition(self):
        return self.getAbsolutePosition() / self.current.lane.getLength()

    def getCoords(self):
        """
        Return the coordinates for the center of this car.
        :return: (float, float) longitude and latitude
        """
        return self.current.lane.getPoint(self.getRelativePosition())

    def getHeadCoords(self):
        """
        Return the coordinates of this car's head.
        :return: (float, float) longitude and latitude
        """
        return self.current.lane.getPoint(self.getRelativePosition() + self.car.length / self.current.lane.getLength())

    def nextCarDistance(self):
        """
        Return the distance to the front car in the same lane or the next lane.
        :return:
        """
        curCar, curDist = self.current.nextCarDistance()
        nextCar, nextDist = self.next.nextCarDistance()
        if curDist < nextDist:
            return curCar, curDist
        else:
            return nextCar, nextDist

    def distanceToStopLine(self):
        if not self.canEnterIntersection():
            return self.getDistanceToIntersection()
        return sys.maxint

    def nextIntersection(self):
        return self.current.lane.road.target

    def previousIntersection(self):
        return self.current.lane.road.getSource()

    def isValidTurn(self):
        if not self.car.nextLane:
            return False
        return True

    def canEnterIntersection(self):
        """
        Determine whether this car can go through the intersection by checking the traffic light of it.
        :return: true if the car can enter the intersection. Otherwise false.
        """
        nextLane = self.car.nextLane
        sourceLane = self.current.lane
        if not nextLane:
            return True
        intersection = self.nextIntersection()
        return intersection.controlSignals.canEnterIntersection(sourceLane, nextLane)

    def getDistanceToIntersection(self):
        """
        Because the current position of this car is the point at the middle of this car, the distance
        to the intersection is:
            the length of the lane - the current position - half of the length of the car
        Note: the distance of this move is already added to this car's position
        :return: the distance from this car's position to the center of the intersection
        """
        distance = self.current.lane.getLength() - self.current.position - (self.car.length / 2.0)
        if not self.isChangingLanes:
            return max(distance, 0)
        else:
            return sys.maxint

    def timeToMakeTurn(self, plannedStep=0):
        """
        If the planned step is larger than the distance from the car's position to the intersection,
        then it is the time to make a turn.
        :param plannedStep: the planned step for this move
        :return: True or False
        """
        return self.getDistanceToIntersection() <= plannedStep

    def moveForward(self, distance):
        """
        :param distance:
        """
        if distance < 0:
            return

        self.current.position += distance
        self.current.updateCarDriveTime()

        if self.timeToMakeTurn() and self.canEnterIntersection() and self.isValidTurn():
            if self.car.alive:
                self.startChangingLanes(self.car.popNextLane())
            else:
                # arrive the destination
                self.release()

        # if self.isChangingLanes:
        if self.isChangingLanes:
            if not self.current.free:
                self.current.release()
            if self.next.free:
                self.next.acquire()
            self.finishChangingLanes()

        if self.current.lane and not self.isChangingLanes and not self.car.nextLane:
            self.car.pickNextLane()

    def switchLane(self, targetLane):
        """
        Switch to the neighbor lane.
        :param targetLane:
        """
        if self.isChangingLanes:
            print "is changing lane"
            return
        if targetLane is None:
            print "no target lane"
            return
        if self.current.lane.road != targetLane.road:
            print "not on the same road"
            return
        if targetLane.canSwitchLane(self.current.position):
            self.current.release()
            self.current.lane = targetLane
            self.current.acquire()

    def startChangingLanes(self, nextLane):
        """
        Change to the nextLane.
        :param nextLane:
        :param distance:
        """
        if self.isChangingLanes:
            print "already changing lane"
        if nextLane is None:
            print "no next lane"
        self.isChangingLanes = True
        self.next.lane = nextLane
        nextLaneCar, nextLaneCarPosition = self.next.nextCarDistance()
        remainderDistance = max(self.current.position - self.current.lane.getLength(), 0)
        nextPosition = min(remainderDistance, nextLaneCarPosition)
        self.next.position = nextPosition

    def finishChangingLanes(self):
        if not self.isChangingLanes:
            print "no lane changing is going on"
        self.next.release()
        self.isChangingLanes = False
        self.current.lane = self.next.lane
        self.current.position = self.next.position
        self.next.lane = None
        self.next.position = 0
        self.current.acquire()

    def release(self):
        if self.current:
            self.current.release()
        if self.next:
            self.next.release()
