from __future__ import division
import sys
import math
import time
from TrafficUtil import *
from Trajectory import Trajectory
from src.trafficSimulator.config import CAR_LENGTH, CAR_WIDTH


class Car(object):
    """
    A class that represents a car.
    """

    SECOND_PER_HOUR = 3600.0

    def __init__(self, lane, position=0, maxSpeed=MAX_SPEED, carType="Car"):
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
        self.alive = True                                   # when this car is going to reach the sink place
                                                            # (or its destination), self.alive = False
        self.delete = False                                 # indicate this car can be deleted
        self.crashed = False                                # indicate this car is crashed or not

        # ====================================================================
        # variables for driving this car
        # ====================================================================
        self.speed = 0                                      # initial speed
        self.maxSpeed = maxSpeed                            # the maximum speed this car can be drove
        self.length = CAR_LENGTH                            # the length (km) of this car
        self.width = CAR_WIDTH
        self.trajectory = Trajectory(self, lane, position)  # manage the moving trajectory of this car
        self.nextLane = None                                # the next lane this can is going to
        self.preferedLane = None                            # the lane that this car is going to switch

        # ====================================================================
        # the destination and route for this care
        # ====================================================================
        self.destination = None                             # the destination for this car
        self.route = None                                   # the path to the destination
        self.routeSetTime = None                            # the last time to set the path
        self.navigator = None                               # Navigator object

    def __eq__(self, other):
        if not other:
            return False
        return self.id == other.id

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
        return self.speed

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
            self.speed = 0

    def setSpeed(self, speed):
        """
        Set the current speed of this car to the given speed parameter.
        The speed cannot exceed the maximum speed of this car and the
        speed limit of the road.
        :param speed: the new speed
        """
        self.speed = min([self.maxSpeed,
                          max(round(speed, 10), 0),
                          self.trajectory.getRoad().getSpeedLimit()])

    # def getDirection(self):
    #     """
    #     Get the current direction of this car.
    #     :return:
    #     """
    #     return self.trajectory.direction  #FIXME: error attribute

    def getNavigation(self):
        """
        Use Navigator to find the shortest route for this car to the destination.
        """
        self.route = self.navigator.navigate(self, self.trajectory.getRoad(), self.destination)
        self.routeSetTime = time.time()

    def release(self):
        """
        delete this car's position from the lane
        """
        self.trajectory.release()

    def getAcceleration(self):
        """
        Get the acceleration factor of this car.
        For the detail of this model, refer to https://en.wikipedia.org/wiki/Intelligent_driver_model
        It will take the following factors into consideration:
        1. the distance to the intersection line
        2. the distance to the front car (if there is a car in front of this car)
        3. the speed difference between the front car and this car
        :return: accelerating factor
        """
        # ===========================================================
        # some constant parameters
        TIME_HEAD_AWAY   = 1.5    # second
        DIST_GAP         = 0.002  # km
        MAX_ACCELERATION = 0.001  # the maximum acceleration (km/s^2)
        MAX_DECELERATION = 0.003  # the maximum deceleration (km/s^2)
        # ===========================================================

        # calculate the free road coefficient
        nextCar, nextDistance = self.trajectory.nextCarDistance()
        distanceToNextCar = max(nextDistance, 0)
        deltaSpeed = (self.speed - nextCar.speed) if nextCar is not None else 0
        speedRatio = self.speed / self.maxSpeed
        freeRoadCoeff = pow(speedRatio, 4)

        # calculate the busy road coefficient
        timeGap = self.speed * TIME_HEAD_AWAY / Car.SECOND_PER_HOUR  # (km/h) * (second/3600) = km
        breakGap = self.speed * deltaSpeed / (2 * math.sqrt(MAX_ACCELERATION * MAX_DECELERATION))
        safeDistance = DIST_GAP + timeGap + breakGap
        if distanceToNextCar > 0:
            distRatio = safeDistance / distanceToNextCar
            busyRoadCoeff = pow(distRatio, 2)
        else:
            busyRoadCoeff = sys.maxint

        # calculate the intersection coefficient
        safeIntersectionDist = 0.001 + timeGap + pow(self.speed, 2) / (2 * MAX_DECELERATION)
        distanceToStopLine = self.trajectory.distanceToStopLine()
        if distanceToStopLine > 0:
            safeInterDistRatio = safeIntersectionDist / distanceToStopLine
            intersectionCoeff = pow(safeInterDistRatio, 2)
        else:
            intersectionCoeff = sys.maxint

        coeff = 1 - freeRoadCoeff - busyRoadCoeff - intersectionCoeff
        return round(MAX_ACCELERATION * coeff, 10)

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

        # choose a quicker lane
        currentLane = self.trajectory.getLane()
        preferedLane = self.getPreferedLane()
        if preferedLane != currentLane:
            self.trajectory.switchLane(preferedLane)

        # if (not self.trajectory.isChangingLanes) and self.nextLane:
        #     currentLane = self.trajectory.current.lane
        #     turnNumber = currentLane.getTurnDirection(self.nextLane)

        # update speed and calculate moving distance
        acceleration = self.getAcceleration()
        self.setSpeed(self.speed + acceleration * second * Car.SECOND_PER_HOUR)
        step = max(self.speed * second / Car.SECOND_PER_HOUR + 0.5 * acceleration * math.pow(second, 2), 0)
        _, nextCarDist = self.trajectory.nextCarDistance()
        nextCarDist = max(nextCarDist, 0)
        step = min(nextCarDist, step)
        if self.trajectory.timeToMakeTurn(step):
            if self.nextLane is None:
                self.pickNextLane()

        if self.alive and self.reachedDestination():
            self.alive = False
            self.delete = True

        self.trajectory.moveForward(step)

    def getPreferedLane(self):
        """
        Choose the quicker lane of current road.
        If the car is going to turn right, then choose the right-most lane
        :return: Lane object
        """
        # if this car is going to turn right, it must be on the right-most lane #TODO

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
        return sampleOne(possibleRoads)

    def pickNextLane(self):
        """

        :return:
        """
        # If there is no routing path or the time for getting the routing path is too
        # long age, update the routing path.
        if not self.route or time.time() - self.routeSetTime > UPDATE_ROUTE_TIME:
            self.getNavigation()

        nextRoad = self.pickNextRoad()

        if not nextRoad:
            return None
        # turnNumber = self.trajectory.current.lane.getTurnDirection(nextRoad)
        # laneNumber = self.getLaneNumber(nextRoad)
        # self.nextLane = nextRoad.lanes[laneNumber]
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
        # return nextRoad.getFastestLane()

    def popNextLane(self):
        nextLane = self.nextLane
        self.nextLane = None
        self.preferedLane = None
        return nextLane

    def setNextLane(self, lane):
        self.nextLane = lane

    def getCurLocation(self):
        """
        Get the car's current coordinates and return it.
        :return:
        """
        pass


class Taxi(Car):
    """
    A class that represents a taxi.
    """

    def __init__(self, lane, position, maxSpeed=MAX_SPEED, carType="Taxi"):
        super(Taxi, self).__init__(lane, position, maxSpeed, carType)
        self.available = True
        self.destRoad = None
        self.destLane = None
        self.destPosition = None
        self.called = False
        self.isTaxi = True

    def setDestination(self, destination):
        """
        Set the destination of this trip.
        :param destination: the coordinates of the destination
        """
        if self.called:
            print "%s is updating its navigation..." % self.id
        super(Taxi, self).setDestination(destination)


    # def setSource(self, source):
    #     """
    #     Set the source coordinates of this trip.
    #     :param source: the coordinates of the source location
    #     """
    #     self.source = source

    def setRandomAvailability(self):
        """
        If the distance (here we simply use direct line distance) between the previous
        location where the availability is changed to False and the current location
        is within some certain distance, then the availability will not change.
        Otherwise, the availability will change randomly.
        :return:
        """
        if self.available or haversine(self.source, self.getCurLocation()) >= 1:  # 1 km
            if random.random() > 0.5:  #TODO: need to choose a better threshold?
                self.available = not self.available

    def setAvailable(self, avail):
        self.available = avail

    def isAvailable(self):
        return self.available

    def beenCalled(self, road, lane, position):
        if not self.available:
            return False
        self.setAvailable(False)
        self.called = True
        self.destRoad = road
        self.destLane = lane
        self.destPosition = position
        return True

    def calledByDestination(self, destination):
        if not self.available:
            return False
        self.setAvailable(False)
        self.called = True
        self.setDestination(destination)
        return True

    def isCalled(self):
        return self.called

    def setNextLane(self, nextLane):
        self.nextLane = nextLane


