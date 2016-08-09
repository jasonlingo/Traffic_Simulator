import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import sys

class AnimatedMap(threading.Thread):
    """
    A decoration class that draw a animated map based on a RealMap object.
    """

    def __init__(self, realMap, env):
        """
        Draw a animated map that shows the movement of cars on the map.
        :param map: a map containing roads, intersection, and cars
        :param env: environment object that controls the map
        """
        self.realMap = realMap
        self.env = env
        self.roads = realMap.getRoads()
        self.intersections = realMap.getIntersections()

        # self.cars = realMap.getCars()
        # self.taxis = realMap.getTaxis()

    def carData(self):
        """
        The method that generates the positions of all cars.
        :return: the cars' positions
        """
        pass

    def plotAnimatedMap(self, fig, ax):
        """
        This method will be continuously run
        :return:
        """
        # self.carPoints, = ax.plot([], [], 'bo', ms=5)
        # self.taxiPoints, = ax.plot([], [], 'yo', ms=5)
        # self.calledTaxiPoints, = ax.plot([], [], 'ro', ms=5)
        # goalLng, goalLat = self.realMap.getGoalPosition()
        # self.goalPoint, = ax.plot([goalLng], [goalLat], 'r*', ms=10)
        print "plotting animated map"
        self.cnt = 0
        board = self.realMap.getBoard()  #[top, bot, right, left]
        latDiff = board[0] - board[1]
        lngDiff = board[2] - board[3]
        self.printCrashCar = False
        self.maxLat = -sys.maxint
        self.minLng = sys.maxint

        def init():
            """
            The initialization step for drawing a animated map. This will be the base plot
            for the animation.
            """
            print "Init animation"

            # plot roads
            for rd in self.roads.values():
                source = rd.getSource()
                target = rd.getTarget()
                if source and target:
                    lngs = [source.center.lng, target.center.lng]
                    lats = [source.center.lat, target.center.lat]
                    self.maxLat = max(self.maxLat, max(lats))
                    self.minLng = min(self.minLng, min(lngs))
                    plt.plot(lngs, lats, color='k')
                else:
                    print "a road is incomplete"

            # plot cars
            self.rightLaneCarPoints, = ax.plot([], [], 'bo', ms=4)
            self.leftLaneCarPoints,  = ax.plot([], [], 'ro', ms=4)

            # plot taxis
            self.taxiPoints, = ax.plot([], [], 'yo', ms=4)
            self.calledTaxiPoints, = ax.plot([], [], 'ro', ms=4)

            # plot goal location
            # goalLng, goalLat = self.realMap.getGoalPosition()
            # self.goalPoint, = ax.plot([goalLng], [goalLat], 'r*', ms=9)

            # plot sink and source points
            # sinkLng = []
            # sinkLat = []
            # sourceLng = []
            # sourceLat = []
            # for p in self.realMap.getSink():
            #     lng, lat = p.getCoords()
            #     sinkLng.append(lng)
            #     sinkLat.append(lat)
            # self.sinkPoint, = ax.plot(sinkLng, sinkLat, 'md', ms=2)
            #
            # for p in self.realMap.getSource():
            #     lng, lat = p.getCoords()
            #     sourceLng.append(lng)
            #     sourceLat.append(lat)
            # self.sourcePoint, = ax.plot(sourceLng, sourceLat, 'kD', ms=2)


            # Notify other thread that the initialization has i
            self.realMap.setAniMapPlotOk(True)

        def animate(i):
            """
            The method is called repeatedly to draw the animation.
            """
            if not self.printCrashCar:
                crashedCar = self.env.getCrashedCar()
                if crashedCar:
                    lngs = []
                    lats = []
                    for car in crashedCar:
                        coords = car.getCoords()
                        lngs.append(coords[0])
                        lats.append(coords[1])
                    self.goalPoint, = ax.plot(lngs, lats, 'y*', ms=8)

            cars = []
            taxis = []
            if self.realMap.checkReset():
                self.carPoints.set_data([], [])
                # self.taxiPoints.set_data([], [])
                # self.calledTaxiPoints.set_data([], [])
                # self.changedSignals.set_data([], [])
            else:
                cars = self.realMap.getCars().values()
                taxis = self.realMap.getTaxis().values()

            rightLaneCarLng = []
            rightLaneCarLat = []
            leftLaneCarLng  = []
            leftLaneCarLat  = []
            for car in cars:
                coords = car.getCoords()
                if car.isOnRightLane():
                    rightLaneCarLng.append(coords[0])
                    rightLaneCarLat.append(coords[1])
                else:
                    leftLaneCarLng.append(coords[0])
                    leftLaneCarLat.append(coords[1])

            # self.carPoints.set_data([car.getCoords()[0] for car in cars], [car.getCoords()[1] for car in cars])
            self.rightLaneCarPoints.set_data(rightLaneCarLng, rightLaneCarLat)
            self.leftLaneCarPoints.set_data(leftLaneCarLng, leftLaneCarLat)

            self.calledTaxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if taxi.called],
                                           [taxi.getCoords()[1] for taxi in taxis if taxi.called])
            self.taxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if not taxi.called],
                                     [taxi.getCoords()[1] for taxi in taxis if not taxi.called])

            # plt.text(self.minLng, self.maxLat, "%d cars" % len(self.realMap.cars))

        ani = animation.FuncAnimation(fig, animate, init_func=init, interval=30, blit=False)
        plt.show()


# =====================================
# For unit testing
# =====================================
# rmap = RealMap("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
# rmap.addRandomCars(10)
# rmap.addRandomTaxi(5)
# rmap.setRandomGoalPosition()
# amap = AnimatedMap(rmap)
# fig, ax = plt.subplots()
# amap.plotAnimatedMap(fig, ax)
