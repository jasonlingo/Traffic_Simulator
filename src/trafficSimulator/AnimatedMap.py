from __future__ import division
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from PIL import Image
import threading
import sys
from DrawUtil import setRectangle
from DrawUtil import GPS_DIST_UNIT
from GoogleMap import getBackgroundMap

# multiple for the car's size
CAR_LEN_MULTI = 16000

colors = {"myYellow": (1, 1, 0.3),
          "calledTaxi": (1, 0, 1)}

# def convertGeoUnit(lat, lng, latBase, lngBase, gpsW, gpsH, imageH, imageW):
#     """
#     Convert geo-coding (lat, lng) to the pixel unit of the base image by
#     computing the ratio of the point to the entire map.
#     The origin for the coordinate system of picture is at the top-left,
#     and bottom-left for the geo-coordinate system (north-west hemisphere).
#     T
#                       north (0~90)
#                          |
#                          |
#      (0~-180) west-------|-------east (0~180)
#                          |
#                          |
#                       south (0~-90)
#
#     :param lat: (float) original latitude
#     :param lng: (float) original longitude
#     :param latBase: (float) the base of the latitude
#     :param lngBase: (float) the base of the longitude
#     :param gpsW: (float) the width of the gps system
#     :param gpsH: (float) the height of the gps system
#     :param imageW: (float) the width of the background image.
#     :param imageH: (float) the height of the background image.
#     :return: the (x, y) position.
#     """
#     heightPos = (lat - latBase) / gpsH * imageH
#     widthPos  = (lng - lngBase) / gpsW * imageW
#     return heightPos, widthPos


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
        self.cars = self.realMap.getCars()
        self.taxis = self.realMap.getTaxis()
        # store the patch (shape) object for cars and taxis
        self.carPatch = {}

        self.cnt = 0
        self.printCrashCar = False
        self.maxLat = -sys.maxint
        self.minLat = sys.maxint
        self.maxLng = -sys.maxint
        self.minLng = sys.maxint
        self.gpsW = None
        self.gpsH = None
        self.imageW = None
        self.imageH = None
        self.flipCoord = True  # when using a photo as the background image, set this to True
        self.MAP_DIST_UNIT = None


    def latToPixel(self, lat):
        return (lat - self.maxLat) / self.gpsH * self.imageH

    def lngToPixel(self, lng):
        return (lng - self.minLng) / self.gpsW * self.imageW

    def plotAnimatedMap(self, fig, ax):
        """
        This method will be continuously run
        :return:
        """
        print "Plotting animated map"

        def init():
            """
            The initialization step for drawing a animated map. This will be the base plot
            for the animation.
            """
            print "Initialize animation"

            # collect gps points of roads
            allLngs = []
            allLats = []
            for rd in self.roads.values():
                source = rd.getSource()
                target = rd.getTarget()
                if source and target:
                    allLngs.append([source.center.lng, target.center.lng])
                    allLats.append([source.center.lat, target.center.lat])
                    self.maxLat = max(self.maxLat, source.center.lat, target.center.lat)
                    self.minLat = min(self.minLat, source.center.lat, target.center.lat)
                    self.maxLng = max(self.maxLng, source.center.lng, target.center.lng)
                    self.minLng = min(self.minLng, source.center.lng, target.center.lng)

            # get map's height and width in GPS unit
            self.gpsH = self.minLat - self.maxLat  # top is the baseline
            self.gpsW = self.maxLng - self.minLng  # left is the baseline

            # get Google static map and show it as a background image
            mapCenter = ((self.maxLat + self.minLat) / 2.0, (self.maxLng + self.minLng) / 2.0)
            baseMapName = getBackgroundMap(mapCenter, abs(self.maxLat - self.minLat), abs(self.maxLng - self.minLng))
            resizedMapName = "./pic/map/resized_map.png"  # TODO: change to parameter

            # adjust the static map size
            baseImg = Image.open(baseMapName)
            width, height = baseImg.size  # width, height
            # ratio = 0.8
            # size = width * ratio, height * ratio
            # baseImg.thumbnail(size, Image.ANTIALIAS)
            marginH = 137  # the pixel size for the margin of the cropped image
            extraH = 0
            extraW = int(extraH * width / height)
            marginW = int(marginH * width / height)
            baseImg.crop((marginW + extraW,
                          marginH + extraH,
                          width - marginW,
                          height - marginH))\
                   .save(resizedMapName, "png")

            img = plt.imread(resizedMapName)
            plt.imshow(img, zorder=0)

            # get image size
            self.imageW, self.imageH = Image.open(resizedMapName).size
            print "resized map's size:", self.imageW, self.imageH

            # convert coordination system
            allLngs = map(lambda x: [self.lngToPixel(x[0]), self.lngToPixel(x[1])], allLngs)
            allLats = map(lambda x: [self.latToPixel(x[0]), self.latToPixel(x[1])], allLats)

            # plot roads
            for i in range(len(allLngs)):
                plt.plot(allLngs[i], allLats[i], color='w', alpha=0.7)

            # create rectangle patches for cars and taxis
            for car in self.cars.values() + self.taxis.values():
                center = car.getCoords()
                newCenter = (self.lngToPixel(center[0]), self.latToPixel(center[1]))
                patch = patches.Rectangle(newCenter, 0, 0,  alpha=1.0)
                self.carPatch[car.id] = patch
                ax.add_patch(patch)

            # plot cars
            self.rightLaneCarPoints, = ax.plot([], [], 'bo', ms=4, zorder=1)
            self.leftLaneCarPoints,  = ax.plot([], [], 'ro', ms=4, zorder=1)

            # plot taxis
            self.taxiPoints, = ax.plot([], [], color=colors["myYellow"], ms=4, zorder=1)
            self.calledTaxiPoints, = ax.plot([], [], color=colors["myYellow"], ms=4, zorder=1)

            # plot goal location
            # goalLng, goalLat = self.realMap.getGoalPosition()
            # self.goalPoint, = ax.plot([goalLng], [goalLat], 'r*', ms=9)

            # ===============================================
            # plot sink and source points
            # ===============================================
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


            # Notify other thread that the initialization has finished
            print "Animated map initialization finished"
            self.realMap.setAniMapPlotOk(True)

        def animate(i):
            """
            The method is called repeatedly to draw the animation.
            :param i: (int) the number of times that this function is called.
            """
            # delete unused patches
            deletePatch = []
            for key in self.carPatch:
                if key not in self.cars and key not in self.taxis:
                    deletePatch.append(key)
            for key in deletePatch:
                del self.carPatch[key]

            # plot crashed cars
            if not self.printCrashCar:
                crashedCar = self.env.getCrashedCar()
                if crashedCar:
                    lngs = []
                    lats = []
                    for car in crashedCar:
                        coords = car.getCoords()
                        lngs.append(self.lngToPixel(coords[0]))
                        lats.append(self.latToPixel(coords[1]))
                    self.goalPoint, = ax.plot(lngs, lats, 'y*', ms=10)

            # plot cars
            for car in self.cars.values() + self.taxis.values():
                if car.crashed:
                    continue
                if car.id in self.carPatch:
                    patch = self.carPatch[car.id]
                else:
                    coords = car.getCoords()
                    newCoords = (self.lngToPixel(coords[0]), self.latToPixel(coords[1]))
                    patch = patches.Rectangle(newCoords, 0, 0, alpha=1.0)
                    self.carPatch[car.id] = patch
                center = car.getCoords()
                newCenter = (self.lngToPixel(center[0]), self.latToPixel(center[1]))
                head = car.getHeadCoords()
                newHead = (self.lngToPixel(head[0]), self.latToPixel(head[1]))
                setRectangle(ax,
                             patch,
                             newCenter,
                             CAR_LEN_MULTI * car.length / GPS_DIST_UNIT * self.gpsH * self.imageH,
                             CAR_LEN_MULTI * car.width / GPS_DIST_UNIT * self.gpsH * self.imageH,
                             newHead, self.flipCoord)
                ax.add_patch(patch)


                if car.isTaxi:
                    if car.called:
                        patch.set_color(colors["calledTaxi"])
                    else:
                        patch.set_color(colors["myYellow"])
                else:
                    if car.isOnRightLane():
                        patch.set_color("r")
                    else:
                        patch.set_color("b")

            # cars = []
            # taxis = []
            # if self.realMap.checkReset():
            #     self.carPoints.set_data([], [])
            #     self.taxiPoints.set_data([], [])
            #     self.calledTaxiPoints.set_data([], [])
            #     self.changedSignals.set_data([], [])
            # else:
            #     cars = self.realMap.getCars().values()
            #     taxis = self.realMap.getTaxis().values()
            #
            # rightLaneCarLng = []
            # rightLaneCarLat = []
            # leftLaneCarLng  = []
            # leftLaneCarLat  = []
            # for car in cars:
            #     coords = car.getCoords()
            #     if car.isOnRightLane():
            #         rightLaneCarLng.append(coords[0])
            #         rightLaneCarLat.append(coords[1])
            #     else:
            #         leftLaneCarLng.append(coords[0])
            #         leftLaneCarLat.append(coords[1])
            #
            # self.rightLaneCarPoints.set_data(rightLaneCarLng, rightLaneCarLat)
            # self.leftLaneCarPoints.set_data(leftLaneCarLng, leftLaneCarLat)
            #
            # self.calledTaxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if taxi.called],
            #                                [taxi.getCoords()[1] for taxi in taxis if taxi.called])
            # self.taxiPoints.set_data([taxi.getCoords()[0] for taxi in taxis if not taxi.called],
            #                          [taxi.getCoords()[1] for taxi in taxis if not taxi.called])


        # interval: draws a new frame every interval milliseconds
        _ = animation.FuncAnimation(fig, animate, init_func=init, interval=30, blit=False)
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
