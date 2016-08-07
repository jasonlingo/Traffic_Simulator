from TrafficUtil import *
from Car import *
from TrafficUtil import *
from RealMap import RealMap
from Pool import Pool
from Road import Road
from Intersection import Intersection
from TrafficSettings import *


class World(object):
    """
    A class that manages the traffic simulator on a map.
    """

    def __init__(self, shapefile):
        """
        :param carNum (int): the total number of cars to be added in the map for this experiment
        :param taxiNum (int): the total number of taxis to be added in the map for this experiment
        :param shapefile (string): the file name of a shapefile that is going to be used for this experiment
        """
        self.realMap = RealMap(shapefile)
        self.roads = self.realMap.getRoads()
        self.intersections = self.realMap.getIntersections()

        # self.onTick = Traffic.bind(self.onTick, self)  # FIXME
        self.carsNum = 0
        self.taxiNum = 0
        self.cars = None
        self.taxis = None
        self.toRemove = []


    # def instantSpeed(self):
    #     """
    #     Calculate the average speed of all the cars.
    #     :return: average speed
    #     """
    #     if not self.cars and not self.taxis:  # no car and taxi
    #         return 0
    #     speeds = [car.speed for car in self.cars] + [taxi.speed for taxi in self.taxis]
    #     if not speeds:
    #         return 0
    #     return sum(speeds) / float(len(speeds))

    def setup(self):
        """
        Create intersection, roads, cars, and taxis
        """
        self.addRandomCar(self.carsNum)
        self.addRandomTaxi(self.taxiNum)

    # def generateMap(self, X, Y, linemax=5, mult=0.8):
    #     self.realMap.createMap()

    # def clear(self):
    #     self.setup({})

    def onTick(self, delta):
        """
        Control the time frame and refresh the traffic signals and cars' movement.
        """
        if delta > 1:
            print "delta > 1"
            return
        self.refreshCars()
        _ref = self.intersections.all()
        for id in _ref:
            intersection = _ref[id]
            intersection.controlSignals.onTick(delta)

        _ref1 = self.cars.all()
        _results = []
        for id in _ref1:
            car = _ref1[id]
            car.move(delta)
            if not car.alive:
                _results.append(self.removeCar(car))
            else:
                _results.append(None)
        return _results


    def refreshCars(self):
        """
        When some cars are disappeared because they are located outside the map, add
        new cars into the map. If the number of cars is more than the limit, remove
        some cars randomly.
        """
        if len(self.cars) < CARS_NUMBER:
            self.addRandomCar(CARS_NUMBER - len(self.cars))
        elif len(self.cars) > CARS_NUMBER:
            self.removeRandomCar(len(self.cars) - CARS_NUMBER)

        if len(self.cars) < TAXI_NUMBER:
            self.addRandomTaxi(TAXI_NUMBER - len(self.cars))
        elif len(self.cars) > TAXI_NUMBER:
            self.removeRandomTaxi(len(self.cars) - TAXI_NUMBER)

    # def addRoad(self, road):
    #     self.roads.append(road)
    #     road.source.roads.push(road)
    #     road.target.inRoads.push(road)
    #     road.update()
    #
    # def getRoad(self, id):
    #     return self.roads.get(id)

    def addRandomCar(self, num):
        """
        Add num random cars in the realMap and set the added cars to self.cars
        :param num: the number of cars to be added to the realMap
        """
        self.realMap.addRandomCars(num)
        self.cars = self.realMap.getCars()

    def getCar(self, id):
        return self.cars.get(id)

    def addRandomTaxi(self, num):
        """
        Add num random taxis in the realMap and set the added cars to self.taxis
        :param num: the number of taxis to be added to the realMap
        """
        self.realMap.addRandomTaxi(num)
        self.taxis = self.realMap.getTaxis()

    # def getTaxi(self, id):
    #     return self.taxis.get(id)

    def removeCar(self, car):
        self.toRemove.append(car.id)
        return self.cars.pop(car)

    def clearTmpRemove(self):
        self.toRemove = []

    def addIntersection(self, intersection):
        self.intersections.append(intersection)

    def getIntersection(self, id):
        return self.intersections.get(id)

    # def addRandomCar(self, n):
    #     for _ in range(n):
    #         road = sample(self.roads)
    #         if road:
    #             lane = sample(road.lanes)
    #             if lane:
    #                 self.addCar(Car(50, lane, 0))
    #
    # def removeRandomCar(self, n):
    #     for _ in range(n):
    #         car = sample(self.cars)
    #         if car:
    #             self.removeCar(car)
    #
    # def addRandomTaxi(self, n):
    #     for _ in range(n):
    #         road = sample(self.roads)
    #         if road:
    #             lane = sample(road.lanes)
    #             if lane:
    #                 self.addCar(Taxi(50, lane, 0))
    #
    # def removeRandomTaxi(self, n):
    #     for _ in range(n):
    #         taxi = sample(self.taxis)
    #         if taxi:
    #             self.removeCar(taxi)