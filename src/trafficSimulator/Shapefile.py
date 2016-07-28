import shapefile as shp
import pygmaps
import webbrowser
import os
from Traffic import RoadType
from Road import Road
from Intersection import Intersection
from Coordinate import Coordinate


class Shapefile(object):
    """
    A class that load road data from a shapefile and output as desired data structure.
    """

    def __init__(self, filename, dataNum):
        """
        :param filename: the filename of a shapefile
        """
        self.ctr = shp.Reader(filename)
        self.shapeRecords = self.ctr.iterShapeRecords()
        self.dataNum = dataNum

        self.roads = {}
        self.intersections = {}

        # the top, bottom, right, and left edge of this map
        self.top = None
        self.bot = None
        self.right = None
        self.left = None

    def getRoads(self):
        """
        Read the shapefile and get all the coordinates of roads.
        :return: a dictionary containing road data
        """
        if not self.roads:
            self.roads = self.readData(RoadType.ROAD)
        return self.roads

    def getIntersections(self):
        """
        Read the shapefile and get all the coordinates of intersections.
        :return: a dictionary containing intersection data
        """
        if not self.intersections:
            self.intersections = self.readData(RoadType.INTERSECTION)
        return self.intersections

    def readData(self, roadType):
        """
        Get the data out according to given road type. The road types include
        'Median Hidden', 'Median Island', 'Parking Garage', 'Road Hidden', 'Alley',
        'Paved Drive', 'Hidden Median', 'Parking Lot', 'trafficSimulator Island', 'Intersection',
        'Road'. The output coordinate will be the center (average of the coordinates)
        of the road type.

        :param roadType: the given road type.
        :return: a dictionary of coordinates for the road type.
        """
        print "Loading", roadType,
        i = 0
        result = {}
        for sh in self.ctr.iterShapeRecords():
            i += 1
            if i % 10000 == 0:  # showing progress
                print ".",
            if i > self.dataNum:
                break
            if sh.record[3] == roadType:
                lats = [p[1] for p in sh.shape.points]
                lnts = [p[0] for p in sh.shape.points]
                centerLats = sum(lats) / float(len(lats)) if len(lats) > 0 else None
                centerLnts = sum(lnts) / float(len(lnts)) if len(lnts) > 0 else None
                center = Coordinate(centerLnts, centerLats)

                maxLat, minLat = max(lats), min(lats)
                maxLnt, minLnt = max(lnts), min(lnts)
                corners = [Coordinate(p[1], p[0]) for p in sh.shape.points if p[1] == maxLat or
                                                                              p[1] == minLat or
                                                                              p[0] == maxLnt or
                                                                              p[0] == minLnt]

                # Find the top, bottom, right, and left of this map
                if self.top is None or self.top < maxLat:
                    self.top = maxLat
                if self.right is None or self.right < maxLnt:
                    self.right = maxLnt
                if self.bot is None or self.bot > minLat:
                    self.bot = minLat
                if self.left is None or self.left > minLnt:
                    self.left = minLnt

                rdInter = self.makeRoads(roadType, corners, center)
                result[rdInter.id] = rdInter

        print ""
        return result

    def makeRoads(self, roadType, corners, center):
        """
        Create a road or intersection according to the given road type.
        :param roadType: indicate a road or an intersection to be created
        :param corners: the corner coordinates of this road or intersection
        :param center: the center coordinates of this road or intersection
        :return: a created road or intersection
        """
        if roadType == RoadType.ROAD:
            return Road(corners, center, None, None)
        elif roadType == RoadType.INTERSECTION:
            return Intersection(corners, center, None)  # FIXME, rect

    def getBoard(self):
        return self.top, self.bot, self.right, self.left

    def plotMap(self, intersections, roads, interCheck=None, roadCheck=None):
        print "Total points:", len(intersections) + len(roads)
        if not intersections and not roads:
            print "not points to plot"
            return

        mymap = pygmaps.maps(intersections[0][0], intersections[0][1], 12)

        for point in roads:
            mymap.addpoint(point[0], point[1], "#00FF00")
        for point in intersections:
            mymap.addpoint(point[0], point[1], "#0000FF")
        for point in interCheck:
            mymap.addpoint(point[0], point[1], "#00FFFF")
        for point in roadCheck:
            mymap.addpoint(point[0], point[1], "#FFFF00")

        mapFilename = "shapefileMap.html"
        mymap.draw('./' + mapFilename)

        # Open the map file on a web browser.
        url = "file://" + os.getcwd() + "/" + mapFilename
        webbrowser.open_new(url)

# =========================================================
# For checking the correctness
# =========================================================
# sh = Shapefile("/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf")
# inter = sh.getIntersections()
# roads = sh.getRoads()
# sh.plotMap(inter.values(), roads.values())
