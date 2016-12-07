import sys
import math
from trafficUtil import Traffic


class Engine(object):
    """
    A car's engine. It calculate the speed.
    """

    def __init__(self, trajectory, maxSpeed):
        self.speed = 0
        self.maxSpeed = maxSpeed
        self.trajectory = trajectory
        self.maxAcceleration = 0.001  # the maximum acceleration (km/s^2)
        self.maxDeceleration = 0.003  # the maximum deceleration (km/s^2)
        self.timeHeadAway = 1.5  # second
        self.distGap = 0.002  # km

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

    def getSpeed(self):
        return self.speed

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
        timeGap = self.speed * self.timeHeadAway / Traffic.SECOND_PER_HOUR  # (km/h) * (second/3600) = km

        # calculate the coefficients for calculating the acceleration
        freeRoadCoeff = self.calcFreeRoadCoeff()
        busyRoadCoeff = self.calcBusyRoadCoeff(timeGap)
        intersectionCoeff = self.calcIntersectionCoeff(timeGap)

        coeff = 1 - freeRoadCoeff - busyRoadCoeff - intersectionCoeff
        return round(self.maxAcceleration * coeff, 10)

    def calcFreeRoadCoeff(self):
        speedRatio = self.speed / self.maxSpeed
        return pow(speedRatio, 4)

    def calcBusyRoadCoeff(self, timeGap):
        nextCar, nextDistance = self.trajectory.nextCarDistance()
        distanceToNextCar = max(nextDistance, 0)
        deltaSpeed = (self.speed - nextCar.getSpeed()) if nextCar is not None else 0
        breakGap = self.speed * deltaSpeed / (2 * math.sqrt(self.maxAcceleration * self.maxDeceleration))
        safeDistance = self.distGap + timeGap + breakGap
        if distanceToNextCar > 0:
            distRatio = safeDistance / distanceToNextCar
            return pow(distRatio, 2)
        else:
            return sys.maxint

    def calcIntersectionCoeff(self, timeGap):
        safeIntersectionDist = 0.001 + timeGap + pow(self.speed, 2) / (2 * self.maxDeceleration)
        distanceToStopLine = self.trajectory.distanceToStopLine()
        if distanceToStopLine > 0:
            safeInterDistRatio = safeIntersectionDist / distanceToStopLine
            return pow(safeInterDistRatio, 2)
        else:
            return sys.maxint