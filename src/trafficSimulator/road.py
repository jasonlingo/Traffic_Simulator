from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

from lane import Lane
from trafficUtil import Traffic
from trafficUtil import RoadType
from drawUtil import calcVectAngle
from drawUtil import haversine
from config import MAX_ROAD_LANE_NUM
from config import MAJOR_ROAD_MIN_LEN
from config import AVG_TIME_PERIOD


class Road(object):
    """
    A class that represents a road. It will connect to intersections and contain lanes.
    """

    def __init__(self, corners, center, source, target, speed=40):
        """
        Create a road that start form the source intersection to the destination intersection.
        :param corners: the four points of the road from the shapefile
        :param center: the average coordinates of this road
        :param source: the source intersection
        :param target: the target intersection
        :param speed: the average speed of this road
        """
        self.corners = corners
        self.center = center
        self.source = source
        self.target = target

        self.top, self.bottom, self.right, self.left = self.parseCorners(corners)
        self.speedLimit = speed
        self.avgSpeed = 0
        self.recentSpeedList = []
        self.id = Traffic.uniqueId(RoadType.ROAD)
        self.lanes = []
        self.lanesNumber = None
        self.length = None
        self.setLength()
        self.targetSide = None
        self.sourceSide = None
        self.targetSideId = 0
        self.sourceSideId = 0
        self.isMajorRoad = self.length >= MAJOR_ROAD_MIN_LEN
        self.update()

        # data structure for calculate the average speed
        self.roadSpeed = RoadSpeed(self)

    def __eq__(self, other):
        if not other:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def parseCorners(self, corners):
        """
        Find the top, bottom, right, and left most coordinates.
        :param corners: the given corners of this road.
        :return: the four coordinates
        """
        lats = [p.getCoords()[1] for p in corners]
        lnts = [p.getCoords()[0] for p in corners]
        maxLat = max(lats)
        minLat = min(lats)
        maxLnt = max(lnts)
        minLnt = min(lnts)
        return maxLat, minLat, maxLnt, minLnt

    def getCars(self):
        carPosition = []
        for lane in self.lanes:
            carPosition.extend(lane.carsPosition.values())
        cars = [cp.car for cp in carPosition if cp.car is not None]
        return cars

    def getAvgTrafficTime(self):
        avgDriveTime = self.roadSpeed.getAvgDriveTime(Traffic.globalTime)
        return avgDriveTime
        # curDriveSpeed = self.getCurAvgSpeed()
        # if curDriveSpeed == 0:
        #     curDriveTime = avgDriveTime
        # else:
        #     curDriveTime = (self.getLength() / self.getCurAvgSpeed()) * Traffic.SECOND_PER_HOUR
        # return PERCENTAGE_FOR_AVG_DRIVE_TIME*avgDriveTime + (1 - PERCENTAGE_FOR_AVG_DRIVE_TIME)*curDriveTime

    def getCurAvgSpeed(self):
        """
        Calculate the average speed from all the cars in this road. If there is no car in this road, then return
        the default speed of this road.
        :return: the average speed (km/h)
        """
        # carPosition = []
        # for lane in self.lanes:
        #     carPosition.extend(lane.carsPosition.values())
        # cars = [cp.car for cp in carPosition if cp.car is not None]
        cars = self.getCars()
        if len(cars) > 0:
            return min(self.speedLimit, sum([car.speed for car in cars]) / len(cars))
        else:
            return self.speedLimit

    def getSpeedLimit(self):
        return self.speedLimit

    def setLength(self):
        """
        Calculate the road length from the source to the target intersections.
        :return: the length of the road.
        """
        if self.source and self.target:
            self.length = haversine(self.source.center, self.target.center)

    def isConnected(self, intersection):
        """
        Check whether this road is connected to a intersection.
        :param intersection:
        :return:
        """
        for cor in intersection.corners:
            if self.bottom <= cor.getCoords()[1] <= self.top and self.left <= cor.getCoords()[0] <= self.right:
                return True
        return False

    def isBlocked(self):
        """
        If all the lanes of this road are blocked, return True, else return False
        :return (boolean):
        """
        for lane in self.lanes:
            if not lane.isBlocked():
                return False
        return True

    def leftMostLane(self):
        if self.lanes:
            return self.lanes[0]

    def rightMostLane(self):
        if self.lanes:
            return self.lanes[-1]

    def setSource(self, source):
        """
        Set the source intersection.
        :param source: Intersection object
        """
        self.source = source
        self.setLength()
        self.update()

    def setTarget(self, target):
        """
        Set the target intersection.
        :param target: Intersection object
        """
        self.target = target
        self.setLength()
        self.update()

    def getSource(self):
        return self.source

    def getTarget(self):
        return self.target

    def getLength(self):
        if not self.length:
            self.setLength()
        return self.length

    def getLanes(self):
        return self.lanes

    def getFastLaneBeforePos(self, pos):
        return reduce(lambda a, b: a if a[1] > b[1] else b,
                      [(lane, lane.getFrontAvgSpeed(pos)) for lane in self.lanes])

    def getFastestLane(self):
        candidateLanes = [lane for lane in self.lanes if not lane.isBlocked()]
        fastestSpeed = 0
        fastestLane = None
        for lane in candidateLanes:
            avgSpeed = lane.getAvgSpeed()
            if avgSpeed > fastestSpeed:
                fastestSpeed = avgSpeed
                fastestLane = lane
        return fastestLane

    def getTurnDirection(self, nextRoad):
        """
        Find the road of the next turn and return the corresponding road order.
        Ex:
              |  ^|
        ______|  1|______
          << 2
        ______     0>>___
              |3 ^|
              |V ^|

        :param nextRoad: the next road
        :return: the turn number
        """
        if self.target != nextRoad.source:
            print "invalid turn"
            sys.exit(2)

        # need to determine the turn to the next road (other)
        roadOrder = []
        sourceVec = np.array(self.getSource().center.getCoords()) - np.array(self.getTarget().center.getCoords())

        # calculate the angle of the turn to each road that connects with the target intersection of current road
        for road in self.target.getOutRoads():
            targetVec = np.array(road.getTarget().center.getCoords()) - np.array(road.getSource().center.getCoords())
            angle = calcVectAngle(sourceVec, targetVec)
            if angle == 0:
                angle = 360
            roadOrder.append((angle, road))

         # sort by the angle in ascending order
        roadOrder.sort()
        for i, roadTup in enumerate(roadOrder):
            if roadTup[1] == nextRoad:
                return i

    def update(self):
        if not self.source or not self.target:
            return

        while len(self.lanes) < MAX_ROAD_LANE_NUM:
            self.lanes.append(Lane(self))

        for lane in self.lanes:
            lane.laneIndex()  # find the index for each lane

    def addCarDriveTime(self, carId, curtTime, pos):
        self.roadSpeed.addCarDriveTime(carId, curtTime, pos)

    def deleteCarDriveTime(self, carId, curtTime, endPos):
        self.roadSpeed.deleteCarDriveTime(carId, curtTime, endPos)

    def updateCarDriveTime(self, carId, pos):
        self.roadSpeed.updateCarDriveTime(carId, pos)


class RoadSpeed(object):
    """
    The class used to calculate average speed a road within certain time period.
    """

    def __init__(self, road):
        self.road = road
        self.driveTimes = []
        self.cars = {}
        self.crashedCar = []

    def addCarDriveTime(self, carId, curtTime, pos):
        """
        Add a record to track the time of a car drives on this road.
        :param carId:
        :param curtTime:
        :param pos: (float) relative position
        """
        driveTime = DriveTime(curtTime, pos, carId)
        self.driveTimes.append(driveTime)
        self.cars[carId] = driveTime

    def deleteCarDriveTime(self, carId, curtTime, endPos):
        """
        When a car leave this road, record the time.
        :param carId:
        :return:
        """
        if carId in self.cars:
            driveTime = self.cars[carId]
            driveTime.endTime = curtTime
            driveTime.endPos = min(endPos, 1)  # because we are using 0~1 to represent the relative position
            del self.cars[carId]

    def updateCarDriveTime(self, carId, pos):
        if carId not in self.cars:
            print "no %s in this road" % carId
            return
        self.cars[carId].curtPos = min(pos, 1)

    def getAvgDriveTime(self, curtTime):
        """
        Calculate the average time for a car to drive pass through this road in recent time.
        If there is no car, return the speed limit of the road.
        :param curtTime:
        :return: average traffic time in second
        """
        # pop those drive time that end more than AVG_TIME_PERIOD ago
        # since the time will re-start from 0 when it reach the limit, check the current time is >= or < the drive time
        expiredDriveTime = []
        for driveTime in self.driveTimes:
            if driveTime.endTime is None:
                continue
            if curtTime >= driveTime.endTime and curtTime - driveTime.endTime > AVG_TIME_PERIOD:
                expiredDriveTime.append(driveTime)
            elif curtTime < driveTime.endTime and Traffic.globalTimeLimit - (driveTime.endTime - curtTime) > AVG_TIME_PERIOD:
                expiredDriveTime.append(driveTime)

        # delete expired DriveTime
        for driveTime in expiredDriveTime:
            self.driveTimes.remove(driveTime)

        times = [x.getTrafficTime(curtTime) for x in self.driveTimes]
        times = [x for x in times if x is not None]
        minTrafficTime = (self.road.getLength() / self.road.speedLimit) * Traffic.SECOND_PER_HOUR
        if times:
            avgTime = sum(times) / len(times)
            return max(avgTime, minTrafficTime)
        else:
            return minTrafficTime

    def setCrash(self, carId):
        driveTime = self.cars[carId]
        self.driveTimes.remove(driveTime)
        self.crashedCar.append(driveTime)
        driveTime.crash = True


class DriveTime(object):

    def __init__(self, startTime, pos, carId):
        """
        :param startTime: (int) the timestamp when the car is entering the road
        :param pos: (float) relative position (0~1)
        """
        self.carId = carId
        self.startTime = startTime
        self.endTime = None
        self.startingPos = pos
        self.curtPos = pos
        self.endPos = None
        self.crash = False

    def getTrafficTime(self, curtTime):
        """
        :param curtTime:
        :return: traffic time in second
        """
        if self.endTime:
            if self.endPos == self.startingPos:
                return None
            return (self.endTime - self.startTime) / (self.endPos - self.startingPos)

        posDiff = self.curtPos - self.startingPos
        if self.startTime <= curtTime:
            timeDiff = curtTime - self.startTime
        else:
            timeDiff = Traffic.globalTimeLimit - (self.startTime - curtTime)

        if posDiff == 0:
            if timeDiff == 0:  # just enter this road, don't count this
                return None
            else:
                posDiff = min(0.5, max(0.1, 1 / timeDiff))  # posDiff: 0.1~0.5

        return timeDiff / posDiff
