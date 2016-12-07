import sys
import math
from TrafficUtil import Traffic

class Engine(object):


    def __init__(self, trajectory, maxSpeed):
        self.speed = 0
        self.maxSpeed = maxSpeed
        self.trajectory = trajectory


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
        TIME_HEAD_AWAY = 1.5  # second
        DIST_GAP = 0.002  # km
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
        timeGap = self.speed * TIME_HEAD_AWAY / Traffic.SECOND_PER_HOUR  # (km/h) * (second/3600) = km
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

    