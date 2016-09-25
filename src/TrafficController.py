import time

from src.trafficSimulator.config import POI_LAMBDA


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
        deltaTime = 0.3
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
            for car in self.cars.values():
                if car.delete:
                    car.release()
                    del self.cars[car.id]
                    print "%s went to the sink point. [%d cars, %d taxis]" % (car.id, len(self.cars), len(self.taxis))

            # make each car move
            for car in self.cars.values():
                car.move(deltaTime)

            # assign a new destination to taxis that arrive their old destinations.
            for taxi in self.taxis.values():
                if taxi.delete:
                    print "%s arrived its destination. Assign a new destination to it." % taxi.id
                    newDestination = self.env.realMap.getRandomDestinatino()
                    taxi.destination = newDestination
                    taxi.delete = False
                    taxi.alive = False

            # make each taxi move
            for taxi in self.taxis.values():
                taxi.move(deltaTime)

            # make traffic light change
            self.env.updateContralSignal(deltaTime)

            time.sleep(0.1)



