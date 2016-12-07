from __future__ import division
import sys
import time

from settings import SPEED_LIMIT_ON_CRASH
from settings import TIME_FOR_ACCIDENT
from trafficSimulator.config import METER_TYPE
from trafficSimulator.config import POI_LAMBDA
from trafficSimulator.config import MAJOR_ROAD_POI_LAMBDA
from trafficSimulator.drawUtil import DistanceUnit
from trafficSimulator.trafficUtil import Traffic
from trafficSimulator.sinkSource import SinkSource
from trafficSimulator.priority import PriorityItemQueue


class TrafficController(object):
    """
    A class that control the traffic of a map. It make each car to move and
    make a random car accident. It also generate car flow into the map.
    """

    def __init__(self, env, carNum, taxiNum, majorRoadCarInitRatio, crashRoad, crashPos, numTopTaxi):
        """
        :param env: environment object.
        :param carNum: number of cars in the beginning
        :param taxiNum: number of taxis in the beginning
        :param majorRoadCarInitRatio: (float) the percentage of the carNum to be generated on the major roads
        :param crashRoad: (str) the road's name for a fixed crash
        :param crashPos: (float) the relative position (0-1) of the crashRoad
        :param numTopTaxi: (int) the number of top taxis that arrive the crash location
        """
        self.env = env
        self.crashRoad = crashRoad
        self.crashPos = crashPos
        self.numTopTaxi = numTopTaxi

        # create random cars and taxis
        majorRoadCarsNum = int((carNum + 1) * majorRoadCarInitRatio)
        self.env.addRandomCars(carNum - majorRoadCarsNum, False)
        self.env.addRandomCars(majorRoadCarsNum, True)
        majorRoadTaxisNum = int((taxiNum + 1) * majorRoadCarInitRatio)
        self.env.addRandomTaxis(taxiNum - majorRoadTaxisNum, False)
        self.env.addRandomTaxis(majorRoadTaxisNum, True)

        self.cars = self.env.getCars()
        self.taxis = self.env.getTaxis()

        self.carCrashed = False
        self.crashedCars = []
        self.calledTaxi = []
        self.arrivedTaxiNum = 0
        self.isCalledTaxiArrived = False

    def run(self):
        """
        Run the traffic simulation:
        1. Make each car and taxi move.
        2. Add taxi and car into the map according to the poisson arrival process.
        3. Make a random car crash. Stop the car by setting it speed to 0 and mark it as crashed.
        4. Change the traffic lights.
        """
        print "Traffic controller is running..."
        time.sleep(5)
        self.env.setResetFlag(False)

        # preTime = time.time()
        deltaTime = 0.3  # unit: second

        preCarNum = len(self.cars)

        while not self.isCalledTaxiArrived or self.arrivedTaxiNum < self.numTopTaxi:
            if abs(len(self.cars) - preCarNum) >= 10:
                print "total number of cars:", len(self.cars)
                preCarNum = len(self.cars)

            # clear the cached average speed of roads in the previous loop.
            self.env.realMap.clearRoadAvgSpeed()  # fixme: delete this

            # increment the global timer
            Traffic.updateGlobalTime(deltaTime)

            # make a car crash at a random or fixed location
            if not self.crashedCars and Traffic.globalTime >= TIME_FOR_ACCIDENT:
                if self.crashRoad:  # pre-defined crash location
                    crashedCar = self.env.fixedCarAccident(self.crashRoad, self.crashPos)
                else:
                    crashedCar = self.env.randomCarAccident()

                if crashedCar:
                    Traffic.carIsCrashed = True
                    # set the speed limit of the road where this crash happens and then
                    # call a taxi to the crash location
                    self.carCrashed = True
                    self.crashedCars.append(crashedCar)
                    self.changeCrashRoadSpeed(crashedCar)
                    self.callTaxiForCrash(crashedCar)

            # add new cars
            self.env.addCarFromSource(POI_LAMBDA)
            self.env.addCarFromMajorRoad(MAJOR_ROAD_POI_LAMBDA)

            # delete cars that is reach a sink intersection
            self.deleteCar()

            # make each car move
            for car in self.cars.values():
                car.move(deltaTime)

            # assign a new destination to taxis that arrive their old destinations.
            self.assignDestinationToTaxis()

            # make each taxi move
            for taxi in self.taxis.values():
                taxi.move(deltaTime)

            # make traffic light change
            self.env.updateContralSignal(deltaTime)

            # time.sleep(0.2)

    def callTaxiForCrash(self, crashedCar):
        crashRoad = crashedCar.trajectory.getRoad()
        crashLoc = SinkSource(None, crashRoad, crashedCar.trajectory.current.position)
        hasCalledTaxi = False
        maxCallTimes = 1  # self.findNearestTaxi should exclude unavailable taxis
        while not hasCalledTaxi and maxCallTimes:
            maxCallTimes -= 1
            nearestTaxi = self.findNearestTaxi(crashLoc)
            if nearestTaxi and self.callTaxi(nearestTaxi, crashLoc):
                nearestTaxi.called = True
                self.calledTaxi.append(nearestTaxi)
                hasCalledTaxi = True
        for taxi in self.taxis.values():
            if taxi not in self.calledTaxi:
                taxi.setDestination(crashLoc)

    def changeCrashRoadSpeed(self, crashedCar):
        crashRoad = crashedCar.trajectory.getRoad()
        crashRoad.speedLimit = SPEED_LIMIT_ON_CRASH
        print "%s crashed on %s at time %d" % (crashedCar.id, crashRoad.id, Traffic.globalTime)
        print "Set the speed limit of %s to %d %s" % (crashRoad.id,
                                                      crashRoad.speedLimit,
                                                      "km/h" if METER_TYPE == DistanceUnit.KM else "mph")

    def deleteCar(self):
        """
        Delete cars that reach their destinations.
        """
        deletedCars = []
        for car in self.cars.values():
            if car.delete:
                car.release()
                deletedCars.append(car.id)
        for carId in deletedCars:
            del self.cars[carId]

    def assignDestinationToTaxis(self):
        """
        If a car crashed, then delete the arrived taxis. Otherwise, assign a new destination to the taxis.
        """
        deleteTaxi = []
        for taxi in self.taxis.values():
            if taxi.delete:
                if self.carCrashed:
                    taxi.release()
                    deleteTaxi.append(taxi)
                    self.arrivedTaxiNum += 1

                    if taxi.called:
                        self.isCalledTaxiArrived = True
                        print "=====>",
                    print "%s arrived the crash location at time %d (total %d taxis arrived)\n" % \
                                                 (taxi.id, Traffic.globalTime, self.arrivedTaxiNum)
                else:
                    if taxi.called:
                        print "\n\n%s arrived the crash location!!\n\n" % taxi.id9
                        taxi.alive = False
                    else:
                        print "%s arrived its destination. Assign a new destination to it." % taxi.id
                        newDestination = self.env.realMap.getRandomDestination()
                        taxi.destination = newDestination
                        taxi.delete = False
                        taxi.alive = True

        # If there is a car crashed, then delete the taxi if it arrives the crash location.
        for taxi in deleteTaxi:
            del self.taxis[taxi.id]

    def callTaxi(self, taxi, dest):
        if taxi.calledByDestination(dest):
            print "Called taxi %s for the crash" % taxi.id
            return True
        else:
            print "Failed to call %s" % taxi.id
            return False

    def findNearestTaxi(self, loc):
        """
        Use Dijkstra algorithm to find an available taxi that is nearest
        (by traffic time) to the loc.

        :param loc: (SinkSource)
        :return: the nearest taxi
        """
        print "Searching taxis =========================================="

          # check if there is a taxi on the same road (behind the crashed car)
        sameRoadTaxi = self.findSameRoadTaxi(loc)
        if sameRoadTaxi is not None:
            return sameRoadTaxi

        # find the fastest taxi on other roads
        quickestTaxi = self.findQuistestTaxi(loc)

        print "=========================================================="
        if quickestTaxi is None:
            print "No taxi available!"
        else:
            return quickestTaxi

    def findSameRoadTaxi(self, loc):
        fastTaxi = [sys.maxint, None]
        for car in loc.road.getCars():
            if car.isTaxi and car.available:
                if car.trajectory.current.position <= loc.position:
                    if not fastTaxi[1] or loc.position - car.trajectory.current.position < fastTaxi[0]:
                        fastTaxi[0] = loc.position - car.trajectory.current.position
                        fastTaxi[1] = car
        if fastTaxi[1]:
            return fastTaxi[1]

    def findQuistestTaxi(self, loc):
        fastTaxi = [sys.maxint, None]
        roadTrafficTime = {}
        frontier = PriorityItemQueue()
        frontier.push(0, loc.road.getSource())

        while frontier.size() > 0 and frontier.peek().priority < fastTaxi[0]:
            curr = frontier.pop()
            for road in curr.item.getInRoads():
                if road in roadTrafficTime:
                    trafficTime = roadTrafficTime[road]
                else:
                    trafficTime = road.getAvgTrafficTime()
                    roadTrafficTime[road] = trafficTime

                for car in road.getCars():
                    if car.isTaxi and car.available:
                        time = curr.priority + (1 - car.trajectory.current.position) * trafficTime
                        if time < fastTaxi[0]:
                            print "found faster %s that can arrive the crash location in %f seconds" % (car.id, time)
                            fastTaxi = (time, car)
                        else:
                            print "     %s is slower (%f second)" % (car.id, time)

                # update time to intersection if the time is quicker
                # if the time is less than the previous calculated time, replace it
                # otherwise, do nothing
                time = curr.priority + trafficTime
                inter = road.getSource()
                itemPriority = frontier.getItemPriority(inter)
                if itemPriority is not None:
                    if itemPriority > time:  # update item priority
                        frontier.removeItemFromQueue(inter)
                        frontier.push(time, inter)
                else:
                    frontier.push(time, inter)

        return fastTaxi[1]
