import time
from trafficSimulator.TrafficUtil import POI_LAMBDA
from trafficSimulator.Navigation import Navigator


class TrafficController(object):
    """
    A class that control the traffic of a map. It make each car to move and
    make a random car accident. It also generate car flow into the map.
    """

    def __init__(self, env, carNum, taxiNum):
        """
        :param env: environment object.
        :param carNum: number of cars in the beginning
        :param taxiNum: number of taxis in the beginning
        """
        self.env = env
        self.env.addRandomCars(carNum)
        self.env.addRandomTaxis(taxiNum)
        self.cars = self.env.getCars()
        self.taxis = self.env.getTaxis()

    def run(self):
        """
        Run the traffic simulation:
        1. Make each car and taxi move.
        2. Add taxi and car into the map according to the poisson arrival process.
        3. Make a random car crash. Stop the car by setting it speed to 0 and mark it as crashed.
        4. Change the traffic lights.
        """
        print "Traffic controller is running..."

        self.env.setResetFlag(False)
        timeToAccident = 0
        TIME_FOR_ACCIDENT = 100
        # preTime = time.time()
        accident = False
        deltaTime = 1
        while True:
            # clear the cached average speed of roads in the previous loop.
            self.env.realMap.clearRoadAvgSpeed()

            # make a random car crash
            if not accident and timeToAccident >= TIME_FOR_ACCIDENT:
                self.env.randomCarAccident()
                accident = True
            if timeToAccident < TIME_FOR_ACCIDENT:
                timeToAccident += 1

            # add new car and taxi
            self.env.addCarFromSource(POI_LAMBDA)

            # delete cars that is reach a sink intersection
            deletedCars = [car.id for car in self.cars.values() if car.delete]
            for carId in deletedCars:
                print "%s went to the sink point" % carId
                del self.cars[carId]

            # make each car move
            for car in self.cars.values():
                car.move(deltaTime)

            # make each taxi move
            for taxi in self.taxis.values():
                taxi.move(deltaTime)

            # make traffic light change
            self.env.updateContralSignal(deltaTime)

            time.sleep(0.1)



