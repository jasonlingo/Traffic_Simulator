import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pygmaps
import webbrowser
import time
from Shapefile import Shapefile
from Road import Road
from Car import *
from src.Dijkstra import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class RealMap(object):
    """
    A class that uses real world road data to construct a map.
    """

    def __init__(self, shapefileName, dataNum):
        """
        1. Initialize a real map according to a shapefile.
        2. Get the information of road and intersection from the parsed shapefile.
        3. Create a map by connecting roads with intersections.
        4. Randomly initialize a goal position

        :param shapefileName: the file name of the given shapefile
        """

        self.she = Shapefile(shapefileName, dataNum)  # parse shapefile
        self.roads = {}
        self.intersections = {}

        self.createMap()

        self.board = self.she.getBoard()  # [top, bot, right, left] of the borders of this map

        self.goalLocation = None          # the car crash's location
        self.setRandomGoalPosition()

        self.cars = {}                    # store all cars' id and instance
        self.taxis = {}                   # store all taxis' id and instance
        self.reset = False                # indicate whether it is in the middle (reset) of experiments
        self.locDict = defaultdict(list)  # recode which car is on which lane
        self.aniMapPlotOK = False         # indicate the map has been plotted
        self.carRunsOk = False            # TODO: may not need this

    def createMap(self):
        """
        Connect intersections with roads. Assume every road has two directions.
        """
        print "creating map"

        i = 0
        start_time = time.time()  # for computing the execution time
        for inter in self.she.getIntersections().values():
            for rd in self.she.getRoads().values():
                # =========================
                # showing progress
                i += 1
                if i % 1000000 == 0:
                    print ".",
                    if i % 50000000 == 0:
                        print ""
                # =========================

                if rd.isConnected(inter):
                    if not rd.getSource():
                        rd.setSource(inter)  # TODO: reduce some distance for intersection?
                    elif not rd.getTarget():
                        rd.setTarget(inter)
                        inter.addInRoad(rd)
                        self.roads[rd.id] = rd
                        sourceInter = rd.getSource()
                        sourceInter.addOutRoad(rd)

                        # add a road for opposite direction
                        opRd = Road(rd.corners, rd.center, rd.getTarget(), rd.getSource())
                        inter.addOutRoad(opRd)
                        sourceInter.addInRoad(opRd)
                        self.roads[opRd.id] = opRd
                        if sourceInter.getOutRoads() and sourceInter.getInRoads() and sourceInter.id not in self.intersections:
                            self.intersections[sourceInter.id] = sourceInter

            if inter.getOutRoads() and inter.getInRoads():
                self.intersections[inter.id] = inter
                if len(inter.getOutRoads()) != len(inter.getInRoads()):
                    print "intersection has different number of out and in roads"

        # add control signal on each intersection
        for inter in self.intersections.values():
            inter.buildControlSignal()

        # examine map
        print ""
        print "total road:", len(self.roads), "; total intersection:", len(self.intersections)
        print "checking map"

        # removing unwanted roads and intersections
        # remove intersections that have not connected to any road
        # remove roads that have not connected to any intersection
        removeRoads = []
        removeInters = []
        for inter in self.intersections.values():
            if len(inter.getInRoads()) == 0 or len(inter.getOutRoads()) == 0:
                removeInters.append(inter)

        for rd in self.roads.values():
            if not rd.getSource() or not rd.getTarget() or not rd.lanes:
                removeRoads.append(rd)

        print "remove", len(removeRoads), "roads and", len(removeInters), "intersections"

        for inter in removeInters:
            del self.intersections[inter.id]
        for rd in removeRoads:
            del self.roads[rd.id]


        # =====================================================================
        # checking map
        # =====================================================================
        for road in self.roads.values():
            if not road.getTarget() or not road.getSource():
                print "Err: incomplete road"
            if not road.lanes:
                print "Err: no lane on a road"
        for inter in self.intersections.values():
            roadNum = len(inter.getOutRoads())
            if roadNum == 0:
                print "Err: intersection has no road"
            for rd in inter.getOutRoads():
                if not rd.lanes:
                    print "Err: road", rd.id, "has no lane"

        allInter = [inter.id for inter in self.intersections.values()]

        for road in self.roads.values():
            if road.target.id not in allInter:
                print "Err: target intersection not found"
                print road.target.getOutRoads()
                print road.target.getInRoads()
                self.intersections[road.target.id] = road.target
            if road.source.id not in allInter:
                print "Err: source intersection not found"
                print road.source.getOutRoads()
                print road.source.getInRoads()
                self.intersections[road.source.id] = road.source

        print "checking ended"
        print "using", (time.time() - start_time), "seconds"

    def getRoads(self):
        if not self.roads:
            self.createMap()
        return self.roads

    def getIntersections(self):
        if not self.intersections:
            self.createMap()
        return self.intersections

    def getBoard(self):
        return self.board

    def randomLaneLocation(self):
        """
        Randomly select one land from a randomly selected road and position (the distance from
        the source point to the picked position.
        :return: the selected lane and position.
        """
        rd = None
        while rd is None:
            tmp = random.choice(self.roads.values())
            if tmp.getSource() and tmp.getTarget():
                rd = tmp
        lane = random.choice(rd.lanes)
        position = random.random() * lane.getLength()
        return lane, position

    def setRandomGoalPosition(self):  # TODO: consider move to Experiment or Environment
        """
        Assign the goal location.
        :param loc:
        :return:
        """
        lane, position = self.randomLaneLocation()
        # lane.road.setAvgSpeed(20)  # FIXME: reduce the speed of the road on which a car accident is located
        goalCar = Car(lane, position)
        self.goalLocation = Trajectory(goalCar, lane, position)
        self.goalLocation.setGoal()
        return self.goalLocation

    def getGoalPosition(self):
        return self.goalLocation.getCoords()

    def getGoalLanePosition(self):
        return self.goalLocation

    def cleanTaxis(self):
        for taxi in self.taxis.values():
            taxi.release()
        self.taxis = {}

    def cleanCars(self):
        for car in self.cars.values():
            car.release()
        self.cars = {}

    def addRandomCars(self, num, carType):
        """
        Add num cars into the self.cars dictionary by their id. If an id already exists in the dictionary, then
        update the dictionary with the car.
        :param num: the total number of cars to be added into the dictionary
        """
        print "realmap add " + carType
        if carType == "car":
            carList = self.cars
            carType = Car
        elif carType == "taxi":
            carList = self.taxis
            carType = Taxi
        else:
            sys.stderr.write("RealMap: car type error:", carType)
            sys.exit(1)

        while len(carList) < num:
            lane, position = self.randomLaneLocation()
            car = carType(lane, position)
            if self.checkOverlap(lane, position, car.length):
                carList[car.id] = car

    # def addRandomTaxi(self, num):
    #     """
    #     Add num taxis into the self.taxis dictionary by their id. If an id already exists in the dictionary, then
    #     update the dictionary with this taxi.
    #     :param num: the total number of taxis to be added into the dictionary
    #     """
    #     while len(self.taxis) < num:
    #         lane, position = self.randomLaneLocation()
    #         if self.checkOverlap(lane, position):
    #             taxi = Taxi(lane, position)
    #             self.taxis[taxi.id] = taxi

    def checkOverlap(self, lane, position, carLength):
        """
        Check whether the picked position for a car is overlapped with existing cars.
        :param locDict: the dictionary records all the cars' position on each lane
        :param lane: the given lane to check
        :param position: the given position to check
        :return: True if the car is not overlapped with existing cars; False otherwise
        """
        half = carLength / lane.getLength()
        for (start, end) in self.locDict[lane]:
            if start <= position + half <= end or start <= position - half <= end:
                return False
        self.locDict[lane].append((position - half, position + half))
        return True

    def getCars(self):
        return self.cars

    def getTaxis(self):
        return self.taxis

    def setResetFlag(self, b):
        self.reset = b
        self.locDict = defaultdict(list)

    def checkReset(self):
        return self.reset

    def setAniMapPlotOk(self, b):
        self.aniMapPlotOK = b

    def isAniMapPlotOk(self):
        return self.aniMapPlotOK

    def setCarRunsOK(self, b):
        self.carRunsOk = b

    def isCarRunsOk(self):
        return self.carRunsOk

    def updateContralSignal(self, delta):
        for inter in self.intersections.values():
            inter.controlSignals.updateSignal(delta)

    def getOppositeRoad(self, road):
        """
        Find the road with opposite direction of the given road
        :param road: the given road
        :return: the road with opposite direction
        """
        source = road.getSource()
        target = road.getTarget()

        for rd in target.getOutRoads():
            if rd.getTarget.id == source.id:
                return rd

    def neighbors(self, intersection):
        """
        Find and return the connected intersections of the given intersection
        :param intersection:
        :return: a list of intersections
        """
        return [road.getTarget() for road in intersection.getOutRoads()]

    def cost(self, sourceIntersection, targetIntersection):
        """
        Calculate the time for a car to go through the road connecting the two given intersections.
        The time is calculated by length / speed
        :param sourceIntersection:
        :param targetIntersection:
        :return: return the traffic time (second)
        """
        road = None
        for rd in sourceIntersection.getOutRoads():
            if rd.getTarget().id == targetIntersection.id:
                road = rd
                break
        curAvgSpd = road.getCurAvgSpeed()
        if curAvgSpd > 0:
            return (road.getLength() / curAvgSpd) * 3600  # convert to second
        else:
            return sys.maxint

    def getRoadsBetweenIntersections(self, source, target):
        """
        Find the roads that connect the two given intersections:
        :param source: intersection
        :param target: intersection
        :return: a list of roads
        """
        roads = []
        for road in source.getOutRoads() + target.getOutRoads():
            if road.getTarget() == target and road.getSource() == source:
                roads.append(road)
            elif road.getSource() == target and road.getTarget() == source:
                roads.append(road)
        return roads

    def getAction(self, pos):
        """
        Find the available actions (turns) for the given LanePostion object.
        :param pos (Road): given location
        :return: list of action (Road)
        """
        targetInter = pos.getTarget()
        sourceInter = pos.getSource()
        roads = [road for road in targetInter.getOutRoads() if road.getTarget() != sourceInter]
        if roads:
            return roads
        else:
            return targetInter.getOutRoads()

    def trafficTime(self, source, destination):
        """
        Calculate the time from the source location to the destination location considering the
        speed limit of every sub-region.
        Using Dijkstra's algorithm.
        Args:
            source: Road
            destination: Road
        Returns: traffic time
        """
        goals = [destination.getTarget(), destination.getSource()]
        time = dijkstraTrafficTime(self, source.getTarget(), goals)
        return time

    def plotMap(self):
        """
        Plot the map according to the roads and intersections.
        """
        print "plotting map"
        if not self.intersections or not self.roads:
            print "no map to plot"
            return

        inter = self.intersections.values()[0]
        mymap = pygmaps.maps(inter.center.lat, inter.center.lng, 12)

        i = 0
        for inter in self.intersections.values():
            if len(inter.getInRoads()) == 1 and len(inter.getOutRoads()) == 1:
                i += 1
                mymap.addpoint(inter.center.lat, inter.center.lng, "#FF00FF")
            else:
                mymap.addpoint(inter.center.lat, inter.center.lng, "#0000FF")
        print "%d intersections have only one road connected" % i

        for rd in self.roads.values():
            if rd.getSource() and rd.getTarget():
                mymap.addpath([(rd.getSource().center.lat, rd.getSource().center.lng),
                               (rd.getTarget().center.lat, rd.getTarget().center.lng)], "#00FF00")

        edges = [(self.she.top, self.she.left), (self.she.top, self.she.right), (self.she.bot, self.she.right), (self.she.bot, self.she.left)]

        mymap.addpath(edges, "#FF00FF")

        mapFilename = "shapefileMap.html"
        mymap.draw('./' + mapFilename)

        # Open the map file on a web browser.
        url = "file://" + os.getcwd() + "/" + mapFilename
        webbrowser.open_new(url)


# =========================================================
# For checking correctness
# =========================================================
rm = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf", 6000)
rm.plotMap()