from __future__ import division
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import math
from trafficSimulator.TrafficSettings import CLOSE_CRASH_LANE, CLOSE_ALL_CRASH_LANES
from QLEnvironment import QLEnvironment
from Settings import GOAL_REWARD
from trafficSimulator.Car import Car
from trafficSimulator.Traffic import CarType
import random


class Environment(QLEnvironment):
    """
    An Environment class that inherits from the QLInterface.
    It implements all the methods for QLearning class's needs.
    """

    def __init__(self, realMap):
        """
        :param realMap (RealMap): the map for this environment
        :return:
        """
        self.realMap = realMap
        # self.goalLocation = self.realMap.getGoalLanePosition()  # Trajectory object #TODO: turn off

        # block the goal road, only allow cars move out of the road
        self.block = None
        if CLOSE_CRASH_LANE:
            self.block = self.closeLane(self.goalLocation.current.lane)

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

    def timeToGoalState(self, fromPos):
        """
        Calculate the time from the given
        :param fromPos: the original position (x, y)
        :return: the time from the original position to the goal state's location
        """
        # TODO: need to replace this method later
        return self.realMap.trafficTime(fromPos, self.goalLocation, None)

    def getAction(self, pos):
        """
        Get the available actions for the given position.
        :param pos: LanePosition
        :return: a list of actions
        """
        return self.realMap.getAction(pos)

    def getReward(self, pos, action):
        """
        Return the Goal reward if the given position is the goal location.
        Otherwise, return the reward for non-goal position-action
        Args:
            pos: Road
            action: Road
        Returns:
            the corresponding reward
        """
        if self.checkArriveGoal(pos):
            return GOAL_REWARD

        # TODO: modelizing
        #reward = 0.0
        # =================
        reward = -1.0 + math.pow(10, -self.realMap.trafficTime(pos, self.goalLocation.current.lane.road) / 100.0)
        # =================
        return reward

    def setReachGoal(self, newBool):
        self.reachGoal = newBool

    def isGoalReached(self):
        return self.reachGoal

    def getGoalLocation(self):
        """
        :return: a Trajectory object containing the lane and position of the goal location
        """
        return self.goalLocation

    def checkArriveGoal(self, pos):
        """
        Check whether the position reaches the goal position. If the given position is
        within the goal +/- 0.2 unit distance, then it reaches the goal location.
        Args:
            pos: Road
        Returns:
            True: if the position is reaching the goal location;
            False: otherwise
        """
        goalRoad = self.goalLocation.current.lane.road
        goalInters = [goalRoad.getTarget(), goalRoad.getSource()]  # two intersections connecting to this road
        if pos.getTarget() in goalInters:
            return True
        if pos.getSource() in goalInters:
            return True
        return False

    def addRandomCars(self, num):
        self.realMap.addRandomCars(num, CarType.CAR)
        self.cars = self.realMap.getCars()

    def addRandomTaxis(self, num):
        self.realMap.addRandomCars(num, CarType.TAXI)
        self.taxis = self.realMap.getTaxis()

    def addCarFromSource(self, poissonLambda):
        self.realMap.addCarFromSource(poissonLambda)

    def randomCarAccident(self):
        if not self.cars:
            return
        crashedCar = random.choice(self.cars.values())
        self.crashedCars.add(crashedCar)
        crashedCar.setCrash(True)

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

    def setCarRunsOK(self, b):
        self.realMap.setCarRunsOK(b)

    def isAniMapPlotOk(self):
        return self.realMap.isAniMapPlotOk()

    def updateContralSignal(self, delta):
        self.realMap.updateContralSignal(delta)

