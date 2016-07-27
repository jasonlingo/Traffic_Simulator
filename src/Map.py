
import matplotlib.pyplot as plt
from Util import PriorityQueue
import random
import math
import sys
import Settings


class Map(object):
    """
    A class that represents a map.
    """

    def __init__(self, sizeX, sizeY):
        """
        Construct a map
        Args:
            sizeX: the length of this map.
            sizeY: the height of this map.
        """
        print "Creating map..."
        self.sizeX = sizeX
        self.sizeY = sizeY

        # initialize the route. False means the position is not a route.
        self.road = [[False for _ in range(sizeY)] for _ in range(sizeX)]

        self.subRegion = []
        self.goalLocation = None

        self.trafficQuery = {}  # for dynamic programming

    def checkRoadPoint(self, x, y):
        """
        Check whether the point at given (x, y) is marked True.
        Args:
            x: x coordinate
            y: y coordinate
        Returns: True/False/None if the range is wrong
        """
        if not (0 <= x < self.sizeX and 0 <= y < self.sizeY):
            return None
        return self.road[int(x)][int(y)]

    def generateMapByDeletion(self, numDelete):
        self.road = [[True for _ in range(self.sizeY)] for _ in range(self.sizeX)]

        failTimes = 0  # used to prevent the situation that there is no any point that can be deleted.
        while numDelete > 0 and failTimes < 10000:
            x = random.randrange(self.sizeX)
            y = random.randrange(self.sizeY)

            if self.checkRoadPoint(x, y):
                shouldDelete = True
                fourPoint = []
                checkedPoint = []
                fourPoint = sorted(self.findNeighbor((x, y)))

                if len(fourPoint) < 2:
                    self.road[x][y] = False
                    numDelete -= 1
                    continue

                self.road[x][y] = False
                for p in fourPoint:
                    for q in fourPoint:
                        if p != q and sorted((p, q)) not in checkedPoint:
                            # print "checked: ", checkedPoint
                            checkedPoint.append(sorted((p, q)))
                            # print "check: ", sorted((p, q))

                            if not self.checkConnected(p, q):
                                shouldDelete = False

                if shouldDelete:
                    self.road[x][y] = False
                    # print "delete road: ", x, y
                    numDelete -= 1
                else:
                    # print "=================================== don't delete: ", x, y
                    failTimes += 1
                    self.road[x][y] = True

    def randomRoadPoint(self):
        """
        Generate a random location on the roads.
        Returns:
        """
        # TODO: change it on road, not only at an intersection.
        while True:
            x = random.randrange(self.sizeX)
            y = random.randrange(self.sizeY)
            if self.road[x][y]:
                return float(x), float(y)

    def trafficTime(self, source, dest, action):
        """
        Calculate the time from the source location to the destination location considering the
        speed limit of every sub-region.
        Using Dijkstra's algorithm.
        Args:
            source:
            dest:
        Returns: traffic time
        """
        # find the state for the source location
        newSource, _ = self.findRoad(source)

        # if the calculation has already been performed before,
        # return the time by querying the dictionary
        key = tuple(sorted((newSource, dest)))
        if key in self.trafficQuery:
            return self.trafficQuery[key]

        times = self.dijkstra(newSource, dest)
        self.trafficQuery[key] = times

        return times

    def dijkstra(self, source, dest):
        """
        The dijkstra algorithm used to find the shortest path from
        Args:
            source: the source point
            dest: the destination
        Returns:
            the time from the source to the destination
        """
        queue = PriorityQueue()  # min queue
        time = {}
        prev = {}

        for x in range(self.sizeX):
            for y in range(self.sizeY):
                if self.road[x][y] and (float(x), float(y)) != source:
                    time[(float(x), float(y))] = sys.maxint
                    prev[(float(x), float(y))] = None
                    queue.push((float(x), float(y)), sys.maxint)

        # Distance from source to source
        time[source] = 0
        queue.push(source, 0)

        while not queue.isEmpty():
            u = queue.pop()
            if u == dest:
                break

            for v in self.findNeighbor(u):
                newTime = time[u] + self.trafficTimeForRoad(u, v)
                if newTime < time[v]:
                    queue.update(v, time[v], newTime)
                    time[v] = newTime
                    prev[v] = u

        return time[dest]

    def trafficTimeForRoad(self, u, v):
        """
        calculate the time to drive on the road segmentation
        Args:
            u: the source point
            v: the destination
        Returns:
            the time of the car to
        """
        subU = self.searchSubRegion(u)
        subV = self.searchSubRegion(v)
        count = 0
        speed = 0
        if subU:
            speed += subU.getSpeed()
            # print "found sub-region U with speed: ", subU.getSpeed()
            count += 1
        if subV:
            speed += subV.getSpeed()
            # print "found sub-region V with speed: ", subV.getSpeed()
            count += 1

        if count > 0:
            speed = speed / float(count)
        else:
            speed = 50

        return 1.0 / speed

    def findNeighbor(self, pos):
        """

        Args:
            pos:

        Returns:

        """
        neighbor = []
        if self.checkRoadPoint(pos[0]+1, pos[1]):
            neighbor.append((pos[0]+1, pos[1]))
        if self.checkRoadPoint(pos[0]-1, pos[1]):
            neighbor.append((pos[0]-1, pos[1]))
        if self.checkRoadPoint(pos[0], pos[1]+1):
            neighbor.append((pos[0], pos[1]+1))
        if self.checkRoadPoint(pos[0], pos[1]-1):
            neighbor.append((pos[0], pos[1]-1))
        return neighbor

    def getAction(self, pos):
        """
        Return the action, for the current position and direction
        Args:
            pos:
        Returns: actions
        """
        actions = []
        result = self.findRoad(pos)
        state, direction = result

        if direction == "|":
            actions = [Settings.NORTH, Settings.SOUTH]
        elif direction == "-":
            actions = [Settings.EAST, Settings.WEST]
        else:
            if self.checkRoadPoint(state[0], state[1]+1):
                actions.append(Settings.NORTH)
            if self.checkRoadPoint(state[0], state[1]-1):
                actions.append(Settings.SOUTH)
            if self.checkRoadPoint(state[0]+1, state[1]):
                actions.append(Settings.EAST)
            if self.checkRoadPoint(state[0]-1, state[1]):
                actions.append(Settings.WEST)

        return actions

    def findRoad(self, pos):
        """
        Find the state that the given position belongs to.
        Args:
            pos: (x, y)
        Returns: (x, y), direction
        """
        # use the left-bottom coordinates as the base position of the state
        base = (math.floor(pos[0]), math.floor(pos[1]))

        interMargin = 0.8

        # check at intersection("+"), horizontal("-"), or vertical("|")
        if base[0] + interMargin <= pos[0]:
            if base[1] + (1 - interMargin) >= pos[1]:
                return (base[0] + 1, base[1]), "+"
            elif base[1] + interMargin <= pos[1]:
                return (base[0] + 1, base[1] + 1), "+"
            else:
                return (base[0] + 1, base[1]), "|"

        elif base[0] + (1 - interMargin) >= pos[0]:
            if base[1] + (1 - interMargin) >= pos[1]:
                return (base[0], base[1]), "+"
            elif base[1] + interMargin <= pos[1]:
                return (base[0], base[1] + 1), "+"
            else:
                return (base[0], base[1]), "|"

        else:
            if base[1] + (1 - interMargin) >= pos[1]:
                return (base[0], base[1]), "-"
            elif base[1] + interMargin <= pos[1]:
                return (base[0], base[1] + 1), "-"
            else:
                print "wrong coordinate: in the middle area"
                return

    def checkSurrounding(self, curPos):
        """
        Find how many points surrounding the given position are marked True.
        Args:
            curPos: The given position
        Returns: number of potins that are marked True.
        """
        surrounding = 0
        if curPos[0] + 1 < self.sizeX and self.road[curPos[0]+1][curPos[1]]:
            surrounding += 1

        if 0 <= curPos[0] - 1 and self.road[curPos[0]-1][curPos[1]]:
            surrounding += 1

        if curPos[1] + 1 < self.sizeY and self.road[curPos[0]][curPos[1]+1]:
            surrounding += 1

        if 0 <= curPos[1] - 1 and self.road[curPos[0]][curPos[1]-1]:
            surrounding += 1

        return surrounding

    def outMap(self):
        # TODO: output direction upside down
        f = open('mapfile', 'w')
        for y in range(self.sizeY):
            string = []
            for x in range(self.sizeX):
                if self.road[x][y]:
                    string.append("*")
                else:
                    string.append(" ")
            f.write("".join(string))
            f.write("\n")

    def showMap(self):
        """
        Plot the roads in the map.
        """
        # add roads
        node = 0
        for x in range(self.sizeX):
            rightX = x + 1
            for y in range(self.sizeY):
                node += 1
                # if node % 100 == 0:
                #     print ".",
                if self.road[x][y]:
                    # print "showmap: ", x, y
                    upY = y + 1
                    if rightX < self.sizeX and self.road[rightX][y]:
                        plt.plot([x, rightX], [y, y], color='k')
                    if upY < self.sizeY and self.road[x][upY]:
                        plt.plot([x, x], [y, upY], color='k')

        # add sub-regions
        for subR in self.subRegion:
            xs = [subR.west, subR.east, subR.east, subR.west, subR.west]
            ys = [subR.north, subR.north, subR.south, subR.south, subR.north]
            plt.plot(xs, ys, color=self.speedColor(subR.getSpeed()), linewidth=2.0, alpha=0.7)
            centerX = (subR.west + subR.east) / 2.0
            centerY = (subR.north + subR.south) / 2.0
            self.label( (centerX, centerY), str(subR.getSpeed()) )

        # set map size
        plt.axis([-1, self.sizeX, -1, self.sizeY]) # (minX, maxX, minY, maxY)


    def label(self, xy, text):
        # y = xy[1] - 0.15  # shift y-value for label so that it's below the artist
        plt.text(xy[0], xy[1], text, ha="center", family='sans-serif', size=14)

    def speedColor(self, speed):
        """
        Return the color for the speed:
          speed >= 80: green (g)
          speed >= 60: blue (b)
          speed <  15: red (r)
          speed <= 40: yellow (y)
        Args:
            speed: the given speed
        Returns: Color name
        """
        if   speed >= 80: return "g"
        elif speed >= 60: return "b"
        elif speed >= 25: return "y"
        else: return "r"

    def checkConnected(self, curPos, targetPos):
        """
        Start from curPos, and check whether it can reach the targetPos.
        Args:
            curPos:
            targetPos:
        Returns: True / False
        """
        # print "curPos: ", curPos, " targetPos: ", targetPos
        mapMark = [[False for _ in range(self.sizeY)] for _ in range(self.sizeX)]
        queue = []

        # print "append: ", curPos
        queue.append(curPos)
        mapMark[curPos[0]][curPos[1]] = True
        firstPoint = True

        while len(queue) > 0:
            point = queue.pop(0)
            # print "check: ", point
            if point == targetPos:
                # print "reached target!!!"
                return True

            north = (point[0], point[1]+1)
            south = (point[0], point[1]-1)
            east = (point[0]+1, point[1])
            west = (point[0]-1, point[1])
            if firstPoint:
                if north != targetPos and 0 <= north[0] < self.sizeX and 0 <= north[1] < self.sizeY and \
                   not mapMark[north[0]][north[1]] and self.road[north[0]][north[1]]:
                    mapMark[north[0]][north[1]] = True
                    # print "append: ", north
                    queue.append(north)

                if south != targetPos and 0 <= south[0] < self.sizeX and 0 <= south[1] < self.sizeY and \
                   not mapMark[south[0]][south[1]] and self.road[south[0]][south[1]]:
                    mapMark[south[0]][south[1]] = True
                    # print "append: ", south
                    queue.append(south)

                if east != targetPos and 0 <= east[0] < self.sizeX and 0 <= east[1] < self.sizeY and \
                   not mapMark[east[0]][east[1]] and self.road[east[0]][east[1]]:
                    mapMark[east[0]][east[1]] = True
                    # print "append: ", east
                    queue.append(east)

                if west != targetPos and 0 <= west[0] < self.sizeX and 0 <= west[1] < self.sizeY and \
                   not mapMark[west[0]][west[1]] and self.road[west[0]][west[1]]:
                    mapMark[west[0]][west[1]] = True
                    # print "append: ", west
                    queue.append(west)

                firstPoint = False
            else:
                if 0 <= north[0] < self.sizeX and 0 <= north[1] < self.sizeY and \
                   not mapMark[north[0]][north[1]] and self.road[north[0]][north[1]]:
                    mapMark[north[0]][north[1]] = True
                    # print "append: ", north
                    queue.append(north)

                if 0 <= south[0] < self.sizeX and 0 <= south[1] < self.sizeY and \
                   not mapMark[south[0]][south[1]] and self.road[south[0]][south[1]]:
                    mapMark[south[0]][south[1]] = True
                    # print "append: ", south
                    queue.append(south)

                if 0 <= east[0] < self.sizeX and 0 <= east[1] < self.sizeY and \
                   not mapMark[east[0]][east[1]] and self.road[east[0]][east[1]]:
                    mapMark[east[0]][east[1]] = True
                    # print "append: ", east
                    queue.append(east)

                if 0 <= west[0] < self.sizeX and 0 <= west[1] < self.sizeY and \
                   not mapMark[west[0]][west[1]] and self.road[west[0]][west[1]]:
                    mapMark[west[0]][west[1]] = True
                    # print "append: ", west
                    queue.append(west)

        return False

    def searchSubRegion(self, pos):
        """
        Find the sub-region that contain the given position.
        Args:
            pos: (x, y)
        Returns: the found sub-region; None if no sub-region contains the position.
        """
        for subRegion in self.subRegion:
            if subRegion.isWithinRegion(pos):
                return subRegion
        return None

    def generateSubRegion(self, num):
        """
        Generate sub-regions with different speed parameter, and store them in the self.subRegion.
        Args:
            num: the total number of sub-regions to be generated.
        """
        iter = 0
        while num > 0:
            iter += 1
            centerX = random.randrange(self.sizeX)
            centerY = random.randrange(self.sizeY)
            maxSide = max(3, Settings.MAX_SUB_REGION_SIDE) # to prevent randrange(1,1) error
            rangeSizeX = random.randrange(2, maxSide)      # the width of this sub-region
            rangeSizeY = random.randrange(2, maxSide)      # the height of this sub-region
            speed = random.choice([random.randrange(10, 40),
                                   random.randrange(60, 100)]) # the speed of this sub-region

            subR = self.Region(min(centerY+rangeSizeY, self.sizeY-1),
                               max(centerY-rangeSizeY, 0),
                               min(centerX+rangeSizeX, self.sizeX-1),
                               max(centerX-rangeSizeX, 0),
                               speed)
            # check overlap
            overlap = False
            for region in self.subRegion:
                if region.isOverlap(subR):
                    overlap = True
                    break

            if not overlap:
                self.subRegion.append(subR)
                num -= 1
            else:
                if iter > 1000:
                    # it becomes very hard to find another un-overlapped sub-region
                    print "It hard to find a non-overlapped sub-region after 1000 trials."
                    break

    def setGoalLocation(self, pos):
        """
        Args:
            pos: (x, y)
        """
        self.goalLocation = pos

    class Region:
        """
        A inner class that represent the information about the sub-regions in
        the generate map.
        """

        def __init__(self, north, south, east, west, speed):
            """
            Args:
                north: the limit for northern side
                south: the limit of southern side
                east: the limit of eastern side
                west: the limit of western side
                speedM: the speed multiplier of this region
            """
            self.north = north
            self.south = south
            self.east = east
            self.west = west
            self.speed = speed

        def isWithinRegion(self, pos):
            """
            Check the given position is within this region.
            Args:
                pos: (x, y)
            Returns: True if the given pos is within this region. Otherwise return False.
            """
            return self.south < pos[1] < self.north and self.west < pos[0] < self.east

        def isOverlap(self, subR):
            """
            Check whether the given sub-region is overlapped with this sub-region.
            Args:
                subR: another sub-region to be checked.
            Returns: True if overlapped; False otherwise.
            """
            if self.west > subR.east or self.east < subR.west or self.north < subR.south or self.south > subR.north:
                return False
            else:
                return True

        def getSpeed(self):
            return self.speed


# if __name__ == '__main__':
#     # Test Map
#     maxX = 50
#     maxY = 50
#     map = Map(maxX, maxY)
#
#     map.generateSubRegion(10)
#     map.generateMapByDeletion(700)
#
#     map.outMap()
#     map.showMap()
#     plt.show()
