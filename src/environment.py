from __future__ import division

from trafficSimulator.fixedRandom import FixedRandom
from trafficSimulator.config import CLOSE_ALL_CRASH_LANES
from trafficSimulator.trafficUtil import CarType
from trafficSimulator.realMap import RealMap
from trafficSimulator.car import Car


class Environment(object):
    """
    This class is the interface between the traffic controller and the RealMap.
    """

    def __init__(self, realMap):
        """
        :param realMap (RealMap): the map for this environment
        :return:
        """
        self.realMap = realMap
        self.block = None  # block the goal road, only allow cars move out of the road
        self.reachGoal = False
        self.cars = {}
        self.taxis = {}
        self.crashedCars = set()

    def randomLocation(self):
        """
        Randomly select one land from a randomly selected road and position (0~1).
        :return: the selected lane and position.
        """
        return self.realMap.randomLaneLocation()

    def closeLane(self, lane):
        """
        Put one Car object as a block at the begin of the lane.
        If CLOSE_ALL_CRASH_LANES == True, close all lanes of the road where a car crash happens
        If CLOSE_ALL_CRASH_LANES == False, only close the the lane where a car crash happens

        :param lane: the given lane to be blocked
        :return: a list of block object
        """
        if CLOSE_ALL_CRASH_LANES:
            block = []
            for la in lane.road.getLanes():
                la.setBlocked(True)
                block.append(Car(la))
            return block
        else:
            lane.setBlocked(True)
            return [Car(lane)]

    def getAction(self, pos):
        """
        Get the available actions for the given position.
        :param pos: LanePosition
        :return: a list of actions
        """
        return RealMap.getAction(pos)

    def setReachGoal(self, newBool):
        self.reachGoal = newBool

    def isGoalReached(self):
        return self.reachGoal

    def addRandomCars(self, num, onMajorRoad=False):
        """
        Add random cars to the map.
        :param num: number of cars to be added.
        """
        self.realMap.addRandomCars(num, CarType.CAR, onMajorRoad)
        self.cars = self.realMap.getCars()

    def addRandomTaxis(self, num, onMajorRoad=False):
        """
        Add random taxis to the map.
        :param num: number of taxis to be added.
        """
        self.realMap.addRandomCars(num, CarType.TAXI, onMajorRoad)
        self.taxis = self.realMap.getTaxis()

    def addCarFromSource(self, poissonLambda):
        self.realMap.addCarFromSource(poissonLambda)

    def addCarFromMajorRoad(self, poissonLambda):
        self.realMap.addCarFromMajorRoad(poissonLambda)

    def fixedCarAccident(self, crashRoad, crashPos):
        crashedCar = self.realMap.fixedCarAccident(crashRoad, crashPos)
        if crashedCar:
            self.crashedCars.add(crashedCar)
            crashedCar.setCrash(True)
            return crashedCar
        return None

    def randomCarAccident(self):
        if not self.cars:
            return
        crashedCar = FixedRandom.choice(self.cars.values())
        self.crashedCars.add(crashedCar)
        crashedCar.setCrash(True)
        return crashedCar

    def getRandomDestination(self):
        return self.realMap.getRandomDestination()

    def getCrashedCar(self):
        return self.crashedCars

    def cleanCars(self):
        self.realMap.cleanCars()
        self.cars = None

    def cleanTaxis(self):
        self.realMap.cleanTaxis()
        self.taxis = None

    def getCars(self):
        return self.cars

    def getTaxis(self):
        return self.taxis

    def setResetFlag(self, b):
        self.realMap.setResetFlag(b)

    def changeContralSignal(self, delta):
        self.realMap.changeContralSignal(delta)

    def updateContralSignal(self, delta):
        self.realMap.updateContralSignal(delta)
