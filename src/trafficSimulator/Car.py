from __future__ import division
import math
from Trajectory import Trajectory
from Traffic import *
from TrafficSettings import CAR_LENGTH
import sys


class Car(object):
    """
    A class that represents a car.
    """

    def __init__(self, lane, position=0, maxSpeed=MAX_SPEED, carType="Car"):
        """
        :param lane:
        :param position: the relative position of this car in the given lane
        :param maxSpeed: km/h
        :return:
        """
        self.id = Traffic.uniqueId(carType)
        self.speed = 0
        #self.width = CAR_WIDTH      # the unit used here is km
        self.length = CAR_LENGTH    # the length (km) of this car
        self.maxSpeed = maxSpeed
        self.trajectory = Trajectory(self, lane, position)
        self.nextLane = None
        self.alive = True
        self.preferedLane = None
        self.isTaxi = False
        self.crashed = False

    def __eq__(self, other):
        if not other:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

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

    def getPosition(self):
        """
        Return the current LanePosition of this car.
        :return: LanePosition object
        """
        return self.trajectory.current

    def setCrash(self, bool):
        self.crashed = bool
        if self.crashed:
            self.speed = 0

    def setSpeed(self, speed):
        """
        Set the current speed of this car to the given speed parameter.
        The speed cannot exceed the maximum speed of this car and the
        speed limit of the road.
        :param speed: the new speed
        """
        # speed cannot exceeds the maximum speed that this car can drive
        self.speed = min(self.maxSpeed, max(round(speed, 10), 0))
        # speed cannot exceeds the road speed limit
        self.speed = min(self.speed, self.trajectory.getRoad().getSpeedLimit())

    # def getDirection(self):
    #     """
    #     Get the current direction of this car.
    #     :return:
    #     """
    #     return self.trajectory.direction  #FIXME: error attribute

    def release(self):
        self.trajectory.release()

    def getAcceleration(self):
        """
        Get the acceleration of the speed of this car.
        For the detail of this model, refer to https://en.wikipedia.org/wiki/Intelligent_driver_model
        :return: accelerating factor
        """
        # some constant parameters
        TIME_HEAD_AWAY   = 1.5    # second
        DIST_GAP         = 0.002  # km
        MAX_ACCELERATION = 0.001  # the maximum acceleration (km/s^2)
        MAX_DECELERATION = 0.003  # the maximum deceleration (km/s^2)

        nextCar, nextDistance = self.trajectory.nextCarDistance()
        distanceToNextCar = max(nextDistance, 0)
        deltaSpeed = self.speed - (nextCar.speed if nextCar is not None else 0)  # TODO: check
        speedRatio = self.speed / self.maxSpeed
        freeRoadCoeff = pow(speedRatio, 4)

        timeGap = self.speed * TIME_HEAD_AWAY / 3600.0  # (km/h) * (second/3600)
        breakGap = self.speed * deltaSpeed / (2 * math.sqrt(MAX_ACCELERATION * MAX_DECELERATION))
        safeDistance = DIST_GAP + timeGap + breakGap
        if distanceToNextCar > 0:
            distRatio = (safeDistance / float(distanceToNextCar))
            busyRoadCoeff = pow(distRatio, 2)
        else:
            busyRoadCoeff = sys.maxint

        safeIntersectionDist = 0.001 + timeGap + pow(self.speed, 2) / (2 * MAX_DECELERATION)
        distanceToStopLine = self.trajectory.distanceToStopLine()
        if distanceToStopLine > 0:
            safeInterDistRatio = (safeIntersectionDist / float(distanceToStopLine if distanceToStopLine > 0 else 0.0001))
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
        if self.crashed:  # crashed car cannot move
            return

        acceleration = self.getAcceleration()
        self.setSpeed(self.speed + acceleration * second * 3600)

        # if (not self.trajectory.isChangingLanes) and self.nextLane:
        #     currentLane = self.trajectory.current.lane
        #     turnNumber = currentLane.getTurnDirection(self.nextLane)

        # choose a quicker lane
        currentLane = self.trajectory.current.lane
        preferedLane = self.getPreferedLane()
        if preferedLane != currentLane:
            self.trajectory.switchLane(preferedLane)

        step = max(self.speed * second / 3600.0 + 0.5 * acceleration * math.pow(second, 2), 0)
        nextCarDist = max(self.trajectory.nextCarDistance()[1], 0)

        step = min(nextCarDist, step)
        if self.trajectory.timeToMakeTurn(step):
            if self.nextLane is None:
                self.pickNextLane()
        self.trajectory.moveForward(step)

    def getPreferedLane(self):
        """
        Choose the faster lane of current road
        :param turnNumber:
        :param currentLane:
        :return:
        """
        # TODO: now it only has at most 2 lanes of a road. when the number of lanes per road
        # is large than 2, then the car can only change to the neighbor lanes.

        # current lane only has this car, no need to switch lane.
        if len(self.trajectory.current.lane.carsPosition) == 1:
            return self.trajectory.current.lane
        return self.trajectory.current.lane.road.getFastestLane()

    def pickNextRoad(self):
        """
        Randomly pick the next road from the outbound roads of the target intersection.
        The car cannot make a U-turn unless there is no other road.
        The car cannot go to a blocked road.

        :return: a randomly picked road.
        """
        intersection = self.trajectory.nextIntersection()
        currentLane = self.trajectory.current.lane
        possibleRoads = [road for road in intersection.outRoads
                         if road.target != currentLane.road.source and not road.isBlocked()]
        if not possibleRoads:
            possibleRoads = [road for road in intersection.getOutRoads()]
            if not possibleRoads:
                print "Err: There is no road to pick"
                return None
        return sample(possibleRoads, 1)[0]

    def pickNextLane(self):
        nextRoad = self.pickNextRoad()
        if not nextRoad:
            return None
        # turnNumber = self.trajectory.current.lane.getTurnDirection(nextRoad)
        # laneNumber = self.getLaneNumber(nextRoad)
        # self.nextLane = nextRoad.lanes[laneNumber]
        self.nextLane = self.getLaneNumber(nextRoad)
        if not self.nextLane:
            print 'cannot pick next lane'

    def getLaneNumber(self, nextRoad):
        """
        Choose a lane that has faster average speed.
        :param nextRoad:
        :return:
        """
        return nextRoad.getFastestLane()

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
        self.destination = destination

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
                # self.setSource(self.getCurLocation())

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

    def isCalled(self):
        return self.called

    def setNextLane(self, nextLane):
        self.nextLane = nextLane


