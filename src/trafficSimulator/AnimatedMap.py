import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import sys
from GoogleMap import getGoogleStaticMap, genGooglemap


def convertGeoUnit(lat, lng, imageWidth, imageHeight):
    """
    Convert geocoding (lat, lng) to the pixel unit of the base image.
    :param lat:
    :param lng:
    :param imageWidth: (float) the width of the background image.
    :param imageHeight: (float) the height of the background image.
    :return: the (x, y) position.
    """
    pass


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

        # get the center of the map
        # maxLat, minLat = -sys.maxint, sys.maxint
        # maxLng, minLng = -sys.maxint, sys.maxint
        # for road in self.roads.values():
        #     sourceLng, sourceLat = road.getSource().getCoords()
        #     targetLng, targetLat = road.getTarget().getCoords()
        #     maxLat = max(maxLat, sourceLat, targetLat)
        #     minLat = min(minLat, sourceLat, targetLat)
        #     maxLng = max(maxLng, sourceLng, targetLng)
        #     minLng = min(minLng, sourceLng, targetLng)
        # self.centerLat = (maxLat + minLat) / 2
        # self.centerLng = (maxLng + minLng) / 2

        # plt.plot([maxLng, maxLng, minLng, minLng, centerLng], [maxLat, minLat, maxLat, minLat, centerLat], color='r')

        # imgFilename = "map.png"
        # getGoogleStaticMap(self.centerLat, self.centerLng, imgFilename)
        # image = plt.imread(imgFilename)
        # plt.imshow(image)
        # plt.axis("off")

        self.printCrashCar = False
        self.maxLat = -sys.maxint
        self.minLng = sys.maxint

        def init():
            """
            The initialization step for drawing a animated map. This will be the base plot
            for the animation.
            """
            print "Init animation"

            self.maxLat = -sys.maxint
            self.minLat = sys.maxint
            self.maxLng = -sys.maxint
            self.minLng = sys.maxint

            # plot roads
            for rd in self.roads.values():
                source = rd.getSource()
                target = rd.getTarget()
                if source and target:
                    lngs = [source.center.lng, target.center.lng]
                    lats = [source.center.lat, target.center.lat]
                    self.maxLat = max(self.maxLat, source.center.lat, target.center.lat)
                    self.minLat = min(self.minLat, source.center.lat, target.center.lat)
                    self.maxLng = max(self.maxLng, source.center.lng, target.center.lng)
                    self.minLng = min(self.minLng, source.center.lng, target.center.lng)
                    plt.plot(lngs, lats, color='k')
                else:
                    print "a road is incomplete"

            # get Google static map
            genGooglemap(self.maxLat, self.minLat, self.minLng, self.maxLng)

            # parameters = genGoogleMapAPIParameter(self.maxLat, self.minLat, self.minLng, self.maxLng)
            # imgFilename = "map.png"
            # getGoogleStaticMap(parameters, imgFilename)
            # image = plt.imread(imgFilename)

            # plot cars
            self.rightLaneCarPoints, = ax.plot([], [], 'bo', ms=4)
            self.leftLaneCarPoints,  = ax.plot([], [], 'ro', ms=4)
            self

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

        # def genGooglemap(topLeft, topRight, botLeft, botRight):
        #     """
        #     Retrieve four google static map images using the four points and use 1/4 port of each image to
        #     make a new map image so that we can know the border of the new map.
        #     :return:
        #     """
        #     maps = ["map1.png", "map2.png"]
        #     for i in range(4):
        #         parameters = genGoogleMapAPIParameter()
        #
        #
        #
        # def genGoogleMapAPIParameter(top, bot, left, right):
        #     parameters = {}
        #
        #     # API key
        #     parameters["key"] = GOOGLE_STATIC_MAP_KEY
        #
        #     # center points
        #     centerLat = (top + bot) / 2
        #     centerLng = (left + right) / 2
        #     parameters["center"] = "%f,%f" % (centerLat, centerLng)
        #
        #     # image's width and height
        #     hwRatio = (top - bot) / (right - left)
        #     width = 640
        #     height = int(min(640, hwRatio * width))
        #     parameters["size"] = "%dx%d" % (width, height)
        #
        #     # zoom
        #     parameters["zoom"] = "13"
        #
        #     # scale
        #     parameters["scale"] = "2"
        #
        #     # markers for top left, top right, bottom left, bottom right
        #     topLeft  = "%f,%f" % (top, left)
        #     topRight = "%f,%f" % (top, right)
        #     botLeft  = "%f,%f" % (bot, left)
        #     botRight = "%f,%f" % (bot, right)
        #     center   = "%f,%f" % (centerLat, centerLng)
        #     parameters["markers"] = "markers=size:tiny|%s|%s|%s|%s|%s" % (topLeft, topRight, botLeft, botRight, center)
        #
        #     # map type: roadmap / satellite / terrain / hybrid
        #     parameters["maptype"] = "roadmap"
        #
        #     for key in parameters:
        #         print "%s=%s" % (key, parameters[key])
        #
        #     return parameters

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

        # interval draws a new frame every interval milliseconds.

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
