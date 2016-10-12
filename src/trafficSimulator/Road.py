from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from Lane import Lane
from TrafficUtil import Traffic, RoadType, calcVectAngle, haversine
from src.trafficSimulator.config import MAX_ROAD_LANE_NUM
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
        return self.roadSpeed.getAvgDriveTime(Traffic.globalTime)

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
        avgSpeed = sum([car.speed for car in cars]) / len(cars) if len(cars) > 0 else self.speedLimit
        return avgSpeed

    def getSpeedLimit(self):
        return self.speedLimit

    # def updateAvgSpeed(self):
    #     """
    #     Calculate the average speed of the recent speed data (most recent 100 records) of this road.
    #     Then store the result to "self.avgSpeed."
    #     """
    #     print "update avg speed:", self.id, self.avgSpeed, "->",
    #     curAvgSpeed = self.getCurAvgSpeed()
    #     deleteSpeed = None
    #     if self.recentSpeedList >= 100:
    #         deleteSpeed = self.recentSpeedList.pop(0)
    #     self.recentSpeedList.append(curAvgSpeed)
    #
    #     if deleteSpeed:
    #         self.avgSpeed = (self.avgSpeed * len(self.recentSpeedList) - deleteSpeed + curAvgSpeed) / len(self.recentSpeedList)
    #     else:
    #         self.avgSpeed = (self.avgSpeed * (len(self.recentSpeedList) - 1) + curAvgSpeed) / len(self.recentSpeedList)
    #
    #     print self.avgSpeed

    def getAvgSpeed(self):
        return max(self.avgSpeed, 0.0)

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

    # def addIntersection(self, intersection):
    #     self.connectedIntersections.append(intersection)

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

    # def getTurnDirection(self, other):
    #     """
    #     Each road has only one lane for now. So it returns 0.
    #     :param other: the next road
    #     :return: the turn number
    #     """
    #     if self.target != other.source:
    #         print "invalid roads"
    #         return
    #     # return (other.sourceSideId - self.targetSideId - 1 + 8) % 4 #FIXME: this is the original version
    #
    #     return random.choice([x for x in range(len(other.lanes))])

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
        # self.sourceSideId = self.source.rect.getSectorId(self.target.rect.center())
        # self.sourceSide = self.source.rect.getSide(self.sourceSideId).subsegment(0.5, 1.0)
        # self.targetSideId = self.target.rect.getSectorId(self.source.rect.center())
        # self.targetSide = self.target.rect.getSide(self.targetSideId).subsegment(0, 0.5)
        # self.lanesNumber = min(self.sourceSide.length, self.targetSide.length)
        # self.lanesNumber = max(2, float(self.lanesNumber) / Traffic.settings.gridSize)
        # sourceSplits = self.sourceSide.split(self.lanesNumber, True)
        # targetSplits = self.targetSide.split(self.lanesNumber)
        # if self.lanes is None or len(self.lanes) < self.lanesNumber:
        #     if self.lanes is None:
        #         self.lanes = []
        #     for i in range(self.lanesNumber):
        #         if self.lanes[i] is None:
        #             self.lanes[i] = Lane(sourceSplits[i], targetSplits[i], self)
        #
        # # results = []
        # for i in range(self.lanesNumber):
        #     self.lanes[i].sourceSegment = sourceSplits[i]
        #     self.lanes[i].targetSegment = targetSplits[i]
        #     self.lanes[i].leftAdjacent = self.lanes[i + 1]
        #     self.lanes[i].rightAdjacent = self.lanes[i - 1]
        #     self.lanes[i].leftmostAdjacent = self.lanes[self.lanesNumber - 1]
        #     self.lanes[i].rightmostAdjacent = self.lanes[0]
            # results.append(self.lanes[i].update())
        # return results
        # if not self.lanes:
        #     self.lanes.append(Lane(self))
        while len(self.lanes) < MAX_ROAD_LANE_NUM:
            self.lanes.append(Lane(self))

        for lane in self.lanes:
            lane.laneIndex()  # find the index for each lane

    def addCarTime(self, carId, curtTime, pos):
        self.roadSpeed.addCarTime(carId, curtTime, pos)

    def deleteCarTime(self, carId, curtTime):
        self.roadSpeed.deleteCarTime(carId, curtTime)

    def updateCarTime(self, carId, pos):
        self.roadSpeed.updateCarTime(carId, pos)

class RoadSpeed(object):
    """
    The class used to calculate average speed a road within certain time period.
    """

    class DriveTime(object):

        def __init__(self, startTime, pos):
            """
            :param startTime: (int) the timestamp when the car is entering the road
            :param pos: (float)
            """
            self.startTime = startTime
            self.endTime = None
            self.curtPos = pos
            self.crash = False

        def getTrafficTime(self, curtTime):
            """
            :param curtTime:
            :return:
            """
            end = self.endTime if self.endTime else curtTime

            pos = self.curtPos
            if self.curtPos == 0:
                if end == self.startTime: # just enter this road, don't count this
                    # self.curtPos = sys.maxint
                    return None
                else:
                    pos = 0.1  # multiply the time by 10 times


            if self.startTime <= end:
                return (end - self.startTime) / pos
            else:
                return (Traffic.globalTimeLimit - (self.startTime - end)) / pos

    def __init__(self, road):
        self.road = road
        self.driveTime = []
        self.cars = {}
        self.crashedCar = []

    def addCarTime(self, carId, curtTime, pos):
        driveTime = self.DriveTime(curtTime, pos)
        self.driveTime.append(driveTime)
        self.cars[carId] = driveTime

    def deleteCarTime(self, carId, curtTime):
        """
        When a car leave this road, record the time.
        :param carId:
        :return:
        """
        if carId in self.cars:
            self.cars[carId].endTime = curtTime
            del self.cars[carId]

    def updateCarTime(self, carId, pos):
        if carId not in self.cars:
            print "no %s in this road" % carId
            return
        self.cars[carId].pos = pos

    def getAvgDriveTime(self, curtTime):
        """
        Calculate the average time for a car to drive pass through this road in recent time.
        If there is no car, return the speed limit of the road.
        :param curtTime:
        :return:
        """
        # pop those drive time that end more than AVG_TIME_PERIOD ago
        while self.driveTime and self.driveTime[0].endTime:
            if curtTime >= self.driveTime[0].endTime and curtTime - self.driveTime[0].endTime > AVG_TIME_PERIOD:
                self.driveTime.pop(0)
            elif curtTime < self.driveTime[0].endTime and sys.maxint - (self.driveTime[0].endTime - curtTime) > AVG_TIME_PERIOD:
                self.driveTime.pop(0)
            else:
                break

        times = [x.getTrafficTime(curtTime) for x in self.driveTime]
        if times:
            return sum([x for x in times if x]) / len(times)
            # return sum( map(lambda x: x.getTrafficTime(curtTime), self.driveTime) ) / len(self.driveTime)
        else:
            return (self.road.getLength() / self.road.speedLimit) * 3600

    def setCrash(self, carId):
        driveTime = self.cars[carId]
        self.driveTime.remove(driveTime)
        self.crashedCar.append(driveTime)
        driveTime.crash = True

