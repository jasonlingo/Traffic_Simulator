from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import math
from trafficUtil import Traffic
from trafficUtil import sampleOne

from trajectory import Trajectory
from config import CAR_LENGTH
from config import CAR_WIDTH
from config import UPDATE_ROUTE_TIME
from config import MAX_SPEED
from src.settings import UPDATE_NAVIGATION
from engine import Engine

class Car(object):
    """
    A class that represents a car.
    """

    def __init__(self, navigator, lane, position=0, maxSpeed=MAX_SPEED, carType="Car"):
        """
        :param lane: the lane that this car is moving on
        :param position: the absolute position of this car in the given lane
        :param maxSpeed: km/h
        :return:
        """
        # ====================================================================
        # basic information and states for this car
        # ====================================================================
        self.id = Traffic.uniqueId(carType)                 # the id for this car
        self.isTaxi = False                                 # indicate this car is a general car or a taxi
        self.called = False                                 # is called for the crashed car
        self.alive = True                                   # when this car is going to reach the sink place
                                                            # (or its destination), self.alive = False
        self.delete = False                                 # indicate this car can be deleted
        self.crashed = False                                # indicate this car is crashed or not

        # ====================================================================
        # variables for driving this car
        # ====================================================================
        self.length = CAR_LENGTH                            # the length (km) of this car
        self.width = CAR_WIDTH
        self.trajectory = Trajectory(self, lane, position)  # manage the moving trajectory of this car
        self.nextLane = None                                # the next lane this can is going to
        self.engine = Engine(self.trajectory, maxSpeed)

        # ====================================================================
        # the destination and route for this care
        # ====================================================================
        self.destination = None                             # the destination for this car
        self.route = None                                   # the path to the destination
        self.routeSetTime = None                            # the last time to set the path
        self.navigator = navigator                          # Navigator object

    def __eq__(self, other):
        if (not other) or (not isinstance(other, Car)):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def setDestination(self, destination):
        """
        Set the destination for this car.
        :param destination: SinkSource object
        """
        self.destination = destination
        self.getNavigation()

    def getCoords(self):
        """
        Return the coordinates of this car.
        :return: (lat, lng), lat and lng represents the latitude and longitude respectively
        """
        return self.trajectory.getCoords()

    def getSpeed(self):
        """
        :return: the speed (km/h)
        """
        return self.engine.getSpeed()

    def getHeadCoords(self):
        """
        Return the coordinates of this car's head.
        :return: (float, float) latitude and longitude.
        """
        return self.trajectory.getHeadCoords()

    def getPosition(self):
        """
        Return the current LanePosition of this car.
        :return: current LanePosition object
        """
        return self.trajectory.current

    def setCrash(self, boolean):
        """
        When a car crashes (boolean = True), set its speed to 0.
        :param boolean:
        """
        self.crashed = boolean
        if self.crashed:
            self.engine.speed = 0

    def setSpeed(self, speed):
        self.engine.setSpeed(speed)

    def getNavigation(self):
        """
        Use Navigator to find the shortest route for this car to the destination.
        """
        self.route = self.navigator.navigate(self, self.trajectory.getRoad(), self.destination)
        self.routeSetTime = Traffic.globalTime

    def release(self):
        """
        delete this car's position from the lane
        """
        self.trajectory.release()

    def move(self, second):
        """
        Calculate the distance of this move by the given time and speed of the car.
        Check whether the car can go the computed distance without hitting front car
        or arriving the intersection.
        If the car is going to arrive at a intersection, check the traffic light and choose
        to go straight, turn right, or left.
        :param second: the given time interval in second
        """
        # crashed or deleted car cannot move
        if self.crashed:
            return

        self.updateNavigation()
        self.switchToQuickerLane()
        step = self.calcMovingDist(second)
        self.makeTurn(step)
        self.setAliveAndDeleteFlags()
        self.trajectory.moveForward(step)

    def updateNavigation(self):
        if self.routeSetTime is None:
            self.getNavigation()
        elif UPDATE_NAVIGATION and self.isTaxi and Traffic.carIsCrashed and self.called:
            if Traffic.globalTime >= self.routeSetTime:
                setRouteTimeDiff = Traffic.globalTime - self.routeSetTime
            else:
                setRouteTimeDiff = Traffic.globalTimeLimit - (self.routeSetTime - Traffic.globalTime)
            if setRouteTimeDiff >= UPDATE_ROUTE_TIME:
                self.getNavigation()

    def switchToQuickerLane(self):
        currentLane = self.trajectory.getLane()
        preferedLane = self.getPreferedLane()
        if preferedLane != currentLane:
            self.trajectory.switchLane(preferedLane)

    def calcMovingDist(self, second):
        acceleration = self.engine.getAcceleration()
        self.setSpeed(self.engine.speed + acceleration * second * Traffic.SECOND_PER_HOUR)
        step = max(self.engine.speed * second / Traffic.SECOND_PER_HOUR + 0.5 * acceleration * math.pow(second, 2), 0)
        _, nextCarDist = self.trajectory.nextCarDistance()
        nextCarDist = max(nextCarDist, 0)
        return min(nextCarDist, step)

    def makeTurn(self, step):
        if self.trajectory.timeToMakeTurn(step):
            if self.isTaxi and UPDATE_NAVIGATION and Traffic.carIsCrashed:
                self.getNavigation()
                self.nextLane = None
            if self.nextLane is None:
                self.pickNextLane()

    def setAliveAndDeleteFlags(self):
        if self.alive and self.reachedDestination():
            self.alive = False
            self.delete = True

    def getPreferedLane(self):
        """
        Choose the quicker lane of current road.
        If the car is going to turn right, then choose the right-most lane
        :return: Lane object
        """
        # current lane only has this car, no need to switch lane.
        if len(self.trajectory.getLane().carsPosition) == 1:
            return self.trajectory.getLane()

        # if the quicker lane's speed is < current lane's speed * 1.2, then keep going on current lane
        # only find the average speed of the front cars
        fastLane, fastSpeed = \
            self.trajectory.getRoad().getFastLaneBeforePos(self.trajectory.getAbsolutePosition() + self.length / 2)
        if fastLane != self.trajectory.getLane() and \
            fastSpeed >= self.trajectory.getLane().getFrontAvgSpeed(self.trajectory.getAbsolutePosition() + self.length / 2):  #
            return fastLane

        return self.trajectory.getLane()  # not change lane

    def reachedDestination(self):
        """
        Check whether this car reached its destination.
        :return: True if reached; False otherwise
        """
        if not self.destination:
            return False
        return self.destination.isReached(self.trajectory.current)

    def isOnRightLane(self):
        return self.trajectory.getLane().isRightLane()

    def pickNextRoad(self):
        """
        If there is a routing path, pick the next road according to the routing path.
        Otherwise, randomly pick one road.

        :return: a Road object
        """
        if self.route:
            targetInter = self.trajectory.getRoad().getTarget()
            while self.route:
                if self.route[0].getSource() == targetInter:
                    # print self.id, "pickNextRoad using route:", self.route[0].id
                    return self.route[0]
                self.route.pop(0)

        # randomly pick one road
        intersection = self.trajectory.nextIntersection()
        currentLane = self.trajectory.getLane()
        possibleRoads = [road for road in intersection.outRoads
                         if road.target != currentLane.road.source and not road.isBlocked()]
        if not possibleRoads:
            possibleRoads = [road for road in intersection.getOutRoads()]
            if not possibleRoads:
                print "[%s]: There is no random road" % self.id
                return None
        nextRoad = sampleOne(possibleRoads)
        return nextRoad

    def pickNextLane(self):
        """
        :return:
        """
        # If there is no routing path, then update the routing path.
        if not self.route:
            self.getNavigation()

        nextRoad = self.pickNextRoad()
        if not nextRoad:
            return None
        self.nextLane = self.getLaneNumber(nextRoad)
        if not self.nextLane:
            print "[%s]: cannot pick next lane" % self.id

    def getLaneNumber(self, nextRoad):
        """
        Choose the same lane (left- or right-most) as the current lane.
        :param nextRoad:
        :return:
        """
        if self.trajectory.getLane().isRightLane():
            return nextRoad.getLanes()[-1]
        else:
            return nextRoad.getLanes()[0]

    def popNextLane(self):
        nextLane = self.nextLane
        self.nextLane = None
        return nextLane

    def setNextLane(self, lane):
        self.nextLane = lane


class Taxi(Car):
    """
    A class that represents a taxi.
    """

    def __init__(self, navigator, lane, position, maxSpeed=MAX_SPEED, carType="Taxi"):
        super(Taxi, self).__init__(navigator, lane, position, maxSpeed, carType)
        self.available = True
        self.destRoad = None
        self.destLane = None
        self.destPosition = None
        self.called = False
        self.isTaxi = True

    def __eq__(self, other):
        if (not other) or (not isinstance(other, Taxi)):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def setDestination(self, destination):
        """
        Set the destination of this trip.
        :param destination: the coordinates of the destination
        """
        super(Taxi, self).setDestination(destination)

    def beenCalled(self, road, lane, position):
        if not self.available:
            return False
        self.available = False
        self.destRoad = road
        self.destLane = lane
        self.destPosition = position
        return True

    def calledByDestination(self, destination):
        if not self.available:
            return False
        self.available = False
        self.setDestination(destination)
        return True

    def isCalled(self):
        return self.called
