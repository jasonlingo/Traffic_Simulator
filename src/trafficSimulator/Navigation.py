import heapq
import sys


class Navigator(object):
    """
    A class that finds the quickest route for a source-destination pair.
    It takes the RealMap and find the quickest route.
    """

    MAX_TIME = 1000000000

    def __init__(self, realMap):
        self.realMap = realMap

    def navigate(self, car, source, destination):
        """
        Use Dijkstra algorithm and current traffic situation to find the quickest route
        for the given source and destination pair.
        :param realMap: (RealMap) the map for this navigator
        :param source: (Road) the road that the car is on
        :param destination: (SinkSource)
        :return: a list of path (roads)
        """
        # since we currently doesn't use multi-thread for each car, we can use heapq for better performance
        heap = []
        times = {}    # key: intersection, value: time
        backPtr = {}  # key: intersection, value: intersection

        sourceInter = source.getTarget()

        if destination.isIntersection():
            targetInter = destination.getIntersection()
        else:
            targetInter = destination.getRoad().getSource()

        times[sourceInter] = 0
        heapq.heappush(heap, (0, sourceInter))

        while heap:
            time, currInter = heapq.heappop(heap)
            time = float(time)

            if currInter == targetInter:
                break

            neighborData = self.realMap.neighborAndTime(currInter)
            # neighborData = self.realMap.neighborAndDistance(currInter)
            for t, nextInter in neighborData:
                newTime = round(min(t + time, Navigator.MAX_TIME), 10)  # prevent key not found
                if nextInter in times:
                    if newTime < float(times[nextInter]):
                        key = (times[nextInter], nextInter)
                        if key in heap:
                            heap.remove(key)
                        heapq.heappush(heap, (newTime, nextInter))
                        times[nextInter] = newTime
                        backPtr[nextInter] = currInter
                else:
                    backPtr[nextInter] = currInter
                    times[nextInter] = newTime
                    heapq.heappush(heap, (newTime, nextInter))

        route = self.extractPath(targetInter, backPtr, car)
        if not destination.isIntersection():
            route.append(destination.getRoad())

        return route

    def extractPath(self, target, backPtr, car):
        """
        Extract the shortest path using the back pointer of each node starting
        from the target node to the source node. Store the extracted nodes reversely.

        :param target: (Intersection) the target intersection
        :param backPtr: (dictionary) the intersection and its back pointer
        :param car: (Car) the car
        :return: a list of path (roads)
        """
        roads = []
        current = target

        while current and current in backPtr:
            preNode = backPtr[current]
            found = False
            for road in preNode.getOutRoads():
                if road.getTarget() == current:
                    roads.insert(0, road)
                    found = True
                    break
            if found:
                current = preNode
            else:
                print "Navigator cannot find a route for %s" % car.id
                return

        return roads


class PathNode(object):
    """
    A class for recording the shortest path when performing the algorithm to find
    the shortest path. It has a back pointer pointing to the previous path.
    Finally, it extract the entire shortest path from the destination to the source
    using the back pointer.
    """

    def __init__(self, inter):
        self.intersection = inter
        self.backPtr = None
