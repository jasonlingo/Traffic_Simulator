import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pygmaps
import webbrowser
from Shapefile import Shapefile
from Road import Road
from Car import *
from src.Dijkstra import *
from SinkSource import SinkSource
import numpy
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from Navigation import Navigator
from config import MAJOR_ROAD_MIN_LEN

# probabilities for edge intersections to be a sink or source places
SINK_PROB = 0.15
SOURCE_PROB = 0.15
SINK_SOURCE_PROB = 0.2

# minimal road length (km) for a sink or source point
MIN_SINK_SOURCE_ROAD_LENGTH = 0.2
ROAD_OFFSET_FOR_SINK_SOURCE_POINT = 0.1


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

        :param shapefileName: the file name of the given shape file.
        :param dataNum: the number of shape file records to be read.
        """
        self.she = Shapefile(shapefileName, dataNum)  # parse shape file
        self.roads = {}
        self.intersections = {}

        self.navigator = Navigator(self)  # navigator for cars

        # self.sinkSource = set()           # the places that can be both sink and source places for adding and deleting cars
        self.sink = set()                 # the places that can only be sink places for deleting cars
        self.source = set()               # the places that can only be source places for adding cars
        self.majorRoadSinkSource = set()  # the sink places on major roads

        self.createMap()                  # create the map by connecting the intersection and roads
        self.majorRoads = []
        self.nonMajorRoads = []
        for road in self.roads.values():
            if road.isMajorRoad:
                self.majorRoads.append(road)
            else:
                self.nonMajorRoads.append(road)

        self.board = self.she.getBoard()  # [top, bot, right, left] of the borders of this map

        self.goalLocation = None          # the car crash's location
        # self.setRandomGoalPosition()    # disable for current version

        self.cars = {}                    # store all cars' id and instance
        self.taxis = {}                   # store all taxis' id and instance
        self.reset = False                # indicate whether it is in the middle (reset) of experiments
        self.locDict = defaultdict(list)  # recode which car is on which lane
        self.aniMapPlotOK = False         # indicate the map has been plotted
        # self.carRunsOk = False            # TODO: may not need this
        self.roadAvgSpeed = {}            # the cache for the average speed of each road


    # ========================================================================
    # Get and set methods
    # ========================================================================
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

    def setRandomGoalPosition(self):  # TODO: consider move to Experiment or Environment
        """
        Assign the goal location.
        :return:
        """
        lane, position = self.randomLaneLocation()
        goalCar = Car(lane, position)
        self.goalLocation = Trajectory(goalCar, lane, position)
        self.goalLocation.setGoal()
        return self.goalLocation

    def getGoalPosition(self):
        if self.goalLocation:
            return self.goalLocation.getCoords()
        return None

    def getGoalLanePosition(self):
        return self.goalLocation

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

    def getCars(self):
        return self.cars

    def getTaxis(self):
        return self.taxis

    def setResetFlag(self, b):
        self.reset = b
        self.locDict = defaultdict(list)

    def setAniMapPlotOk(self, b):
        self.aniMapPlotOK = b

    def isAniMapPlotOk(self):
        return self.aniMapPlotOK

    def getSink(self):
        return self.sink

    def getSource(self):
        return self.source

    @classmethod
    def getAction(cls, pos):
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


    # ========================================================================
    # other methods
    # ========================================================================

    def createMap(self):
        """
        Connect intersections with roads. Assume every road has two directions.
        """
        print "Creating map"

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
                if len(inter.getOutRoads()) != len(inter.getInRoads()):
                    print "intersection has different number of out and in roads"
                    continue
                self.intersections[inter.id] = inter

        print ""
        print "total road:", len(self.roads), "; total intersection:", len(self.intersections)

        self.buildTrafficLight()
        self.createSinkSourcePlace()
        self.examineMap()

        print "Using", (time.time() - start_time), "seconds"


    def createS2Map(self):
        """
        Create the map by utilizing the Google S2 algorithm.
        (https://docs.google.com/presentation/d/1Hl4KapfAENAOf4gv-pSngKwvS_jwNVHRPZTTDzXXn6Q/view?pli=1#slide=id.i95)
        :return:
        """
        pass

    def buildTrafficLight(self):
        """
        add control signal on each intersection
        """
        for inter in self.intersections.values():
            inter.buildControlSignal()

    def examineMap(self):
        """
        Examine the map. Check each road has connected to intersections.
        """
        print "Checking map"

        # removing unwanted roads and intersections:
        # (1) remove intersections that have not connected to any road
        # (2) remove roads that have not connected to any intersection
        removeRoads = []
        removeInters = []
        for inter in self.intersections.values():
            if len(inter.getInRoads()) == 0 or len(inter.getOutRoads()) == 0:
                removeInters.append(inter)

        for rd in self.roads.values():
            if not rd.getSource() or not rd.getTarget() or not rd.lanes:
                removeRoads.append(rd)

        if len(removeRoads) > 0 or len(removeInters) > 0:
            print "remove", len(removeRoads), "roads and", len(removeInters), "intersections"

        for inter in removeInters:
            del self.intersections[inter.id]
        for rd in removeRoads:
            del self.roads[rd.id]
        del removeInters
        del removeRoads

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
        del allInter

        print "Checking ended"

    def createSinkSourcePlace(self):
        """
        Create sink and source place for the car to show up and disappear.
        Every intersection can be a sink and source place.
        For a region surrounded by roads, randomly pick one point on the edges as the
        sink and source place for the region.
        :return:
        """
        if not self.sink or not self.source:
            self.sink = set()
            self.source = set()
            # self.sinkSource = set()
            self.assignSinkSourceOnIntersection()
            self.assignSinkSourceOnRoad()
            self.assignSinkSourceOnMajorRoad()
        print "%d sinks" % len(self.sink)
        print "%d sources" % len(self.source)

    def assignSinkSourceOnIntersection(self):
        """
        For those intersections that have only one out road, mark them both
        sink and source points.
        for other intersections, assign a sink or source point, or both to them according
        to the random probabilities.
        """
        for inter in self.intersections.values():
            point = SinkSource(inter)
            if len(inter.getInRoads()) == 1:
                self.sink.add(point)
                self.source.add(point)
            # else:
            #     rand = random.random()
            #     if rand < SINK_PROB:
            #         self.sink.add(point)
            #     elif rand < SINK_PROB + SOURCE_PROB:
            #         self.source.add(point)
            #     elif rand < SINK_PROB + SOURCE_PROB + SINK_SOURCE_PROB:
            #         self.sink.add(point)
            #         self.source.add(point)

    def assignSinkSourceOnRoad(self):
        """
        For each surrounded region, add one sink and source point on one of the roads
        that encloses the region.
        Randomly pick a intersection and sse BFS method to expand the search. When encounter
        a visited road, then add a sink-source point to the road.
        """
        if not self.intersections:
            return
        visited = set()
        queue = []

        start = self.intersections[random.choice(self.intersections.keys())]
        visited.add(start.id)
        queue.append(start)
        while queue:
            currInter = queue.pop(0)
            for road in currInter.getOutRoads():
                nextInter = road.getTarget()
                if nextInter.id in visited:
                    if road.getLength() >= MIN_SINK_SOURCE_ROAD_LENGTH:
                        # Pick the random position on the road. It is a absolute distance.
                        # We also prevent that the random position be set near the intersections by
                        # using a ROAD_OFFSET_FOR_SINK_SOURCE_POINT
                        position = (ROAD_OFFSET_FOR_SINK_SOURCE_POINT +
                                   random.random() * (1 - 2 * ROAD_OFFSET_FOR_SINK_SOURCE_POINT)) * road.getLength()
                        point = SinkSource(None, road, position)
                        self.sink.add(point)
                        self.source.add(point)
                else:
                    visited.add(nextInter.id)
                    queue.append(nextInter)

    def assignSinkSourceOnMajorRoad(self):
        for road in self.roads.values():
            # if a road connects two major roads, then mark it as a major road
            connectedInRoad = map(lambda x: x.isMajorRoad, road.getSource().getInRoads())
            connectedOutRoad = map(lambda x: x.isMajorRoad, road.getTarget().getOutRoads())
            if road.isMajorRoad or (True in connectedInRoad and True in connectedOutRoad):
                road.isMajorRoad = True
                sinkSourceNum = int(road.getLength() / MAJOR_ROAD_MIN_LEN)
                addedSinkSourceNum = 0
                while addedSinkSourceNum <= sinkSourceNum:
                    point = SinkSource(None, road, addedSinkSourceNum * MAJOR_ROAD_MIN_LEN)
                    self.majorRoadSinkSource.add(point)
                    addedSinkSourceNum += 1

    def randomLaneLocation(self, onMajorRoad=False):
        """
        Randomly select one land from a randomly selected road and position (the distance from
        the source point to the picked position.

        :param onMajorRoad: (boolean) indicate whether the cars are generated on major roads
        :return: the selected lane and position.
        """
        if onMajorRoad:
            roads = self.majorRoads
        else:
            roads = self.nonMajorRoads

        road = None
        while road is None:
            tmp = random.choice(roads)
            if tmp.getSource() and tmp.getTarget():
                road = tmp
        lane = random.choice(road.getLanes())
        position = random.random() * lane.getLength()  # TODO: check no car at that position
        return lane, position

    def cleanTaxis(self):
        for taxi in self.taxis.values():
            taxi.release()
        self.taxis = {}

    def cleanCars(self):
        for car in self.cars.values():
            car.release()
        self.cars = {}

    def clearRoadAvgSpeed(self):
        self.roadAvgSpeed.clear()

    def addRandomCars(self, num, carType, onMajorRoad):
        """
        Add num cars into the self.cars dictionary by their id. If an id
        already exists in the dictionary, then update the dictionary with
        the car.
        For each car, also add a destination for it.

        :param num: the total number of cars to be added into the dictionary
        :param carType: the type of car (taxi or car) to be added
        :param onMajorRoad: indicate the cars are added on major roads
        """
        print "realmap add " + carType
        if carType == CarType.CAR:
            carList = self.cars
            carType = Car
        elif carType == CarType.TAXI:
            carList = self.taxis
            carType = Taxi
        else:
            sys.stderr.write("RealMap: car type error: %s" % carType)
            sys.exit(1)

        while num:
            lane, position = self.randomLaneLocation(onMajorRoad)
            car = carType(lane, position)
            if self.checkOverlap(lane, position, car.length):
                car.destination = sampleOne(self.sink)
                car.navigator = self.navigator
                carList[car.id] = car
                num -= 1

    def addCarFromSource(self, posLambda):
        self.addCarFromGivenSource(self.source, posLambda)

    def addCarFromMajorRoad(self, posLambda):
        self.addCarFromGivenSource(self.majorRoadSinkSource, posLambda)

    def addCarFromGivenSource(self, sources, posLambda):
        """
        For each sink-source intersection, get a number of new cars according to
        the poisson arrival process. Choose one lane from the out road of the
        intersection and add a car if there is not car at the position.
        """
        for s in sources:
            numCar = numpy.random.poisson(posLambda)  # number of cars to be added at this source point
            if numCar == 0:
                continue
            addedCar = 0
            if s.isIntersection():  # may have multiple roads to choose from
                inter = s.getIntersection()
                for i in range(2 * numCar):  # try twice of the number of new cars since some picked lanes are filled with cars
                    road = sampleOne(inter.getOutRoads())
                    lane = sampleOne(road.getLanes())
                    addCar = True
                    for car in lane.getCars():
                        if car.trajectory.getAbsolutePosition() < CAR_LENGTH:
                            # print "front car is too close to the new car"
                            addCar = False
                            break
                    if addCar:
                        addedCar += 1
                        destination = sampleOne(self.sink)
                        newCar = Car(lane, 0)
                        newCar.navigator = self.navigator
                        newCar.setDestination(destination)
                        self.cars[newCar.id] = newCar
                        print "Add a new car: %s. [%d cars, %d taxis]" %\
                            (newCar.id, len(self.cars), len(self.taxis))
                        if addedCar == numCar:
                            break
            else:
                road, pos = s.getRoadPos()
                absolutePos = pos * road.getLength()
                for lane in road.getLanes()[::-1]:  # when a car goes into the road, it probably is on the right-most lane
                    addCar = True
                    for car in lane.getCars():
                        if absolutePos - CAR_LENGTH < car.trajectory.getAbsolutePosition() < absolutePos + CAR_LENGTH:
                            # print "front car is too close to the new car"
                            addCar = False
                            break
                    if addCar:
                        addedCar += 1
                        destination = sampleOne(self.sink)
                        newCar = Car(lane, pos)
                        newCar.navigator = self.navigator
                        newCar.setDestination(destination)
                        self.cars[newCar.id] = newCar
                        newCar.destination = sampleOne(self.sink)
                        print "Add a new car: %s. [%d cars, %d taxis]" %\
                              (newCar.id, len(self.cars), len(self.taxis))
                        if addedCar == numCar:
                            break

    def fixedCarAccident(self, crashRoad, crashPos):
        """
        Add a crashed car on the given position.
        :param crashRoad: (str) road for a crash
        :param crashPos: (float) relative position for the crash on the road
        :return:
        """
        if crashRoad not in self.roads:
            print "%s doesn't exist!!"
            exit(0)
        road = self.roads[crashRoad]
        lane = road.getLanes()[0]
        car = Car(lane, crashPos * road.getLength())
        if self.checkOverlap(lane, crashPos, car.length):
            car.destination = sampleOne(self.sink)
            car.navigator = self.navigator
            self.cars[car.id] = car
            return car
        else:
            return None

    def getRandomDestination(self):
        return sampleOne(self.sink)

    def checkOverlap(self, lane, position, carLength):
        """
        Check whether the picked position for a car is overlapped with existing cars.
        :param locDict: the dictionary records all the cars' position on each lane
        :param lane: the given lane to check
        :param position: the given position to check
        :return: True if the car is not overlapped with existing cars; False otherwise
        """
        half = carLength / lane.getLength()
        for start, end in self.locDict[lane]:
            if start <= position + half <= end or start <= position - half <= end:
                return False
        self.locDict[lane].append((position - half, position + half))
        return True

    def checkReset(self):
        return self.reset

    def updateContralSignal(self, delta):
        for inter in self.intersections.values():
            inter.controlSignals.updateSignal(delta)

    def neighbors(self, intersection):
        """
        Find and return the connected intersections of the given intersection
        :param intersection:
        :return: a list of intersections
        """
        return [road.getTarget() for road in intersection.getOutRoads()]

    def neighborAndTime(self, intersection):
        """
        Return a list of neighbor along with the time from the given intersection to
        the neighbor intersections.
        :param intersection: (Intersection)
        :return: a list of tuple (time, neighbor intersection)
        """
        nbs = []
        for road in intersection.getOutRoads():
            if road not in self.roadAvgSpeed:
                self.roadAvgSpeed[road] = road.getCurAvgSpeed()
            # since the time only be used for comparison, no need to convert it to second
            # currently it is calculated by distance (km) / speed (km/hour) = hour
            time = (road.getLength() / float(self.roadAvgSpeed[road])) if self.roadAvgSpeed[road] > 0 else Navigator.MAX_TIME
            nbs.append((time, road.getTarget()))
        return nbs

    def neighborAndDistance(self, intersection):
        """
        Return a list of neighbor along with the time from the given intersection to
        the neighbor intersections.
        :param intersection: (Intersection)
        :return: a list of tuple (time, neighbor intersection)
        """
        nbs = []
        for road in intersection.getOutRoads():
            nbs.append((road.getLength(), road.getTarget()))
        return nbs

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

    def getPathToDestination(self, source, destination):
        """
        Get the quickest path from the source to the destination by using a Dijkstra algorithm.

        :param source:
        :param destination:
        :return: a list of roads
        """
        pass #TODO

    @classmethod
    def getOppositeRoad(cls, road):
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

    # =========================================================================
    # Just for checking the map representation
    # =========================================================================
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
            if inter in self.sinkSource:
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
# rm = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf", 6000)
# rm.plotMap()