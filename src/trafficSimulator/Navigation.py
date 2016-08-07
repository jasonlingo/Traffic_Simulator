import heapq


class Navigator(object):
    """
    A class that finds the quickest route for a source-destination pair.
    It takes the RealMap and find the quickest route.
    """

    def __init__(self, realMap):
        self.realMap = realMap

    def navigate(self, car, source, destination):
        """
        Use Dijkstra algorithm and current traffic situation to find the quickest route
        for the given source and destination pair.
        :param realMap: (RealMap) the map for this navigator
        :param source: (road)
        :param destination: (SinkSource)
        :return: a list of path (roads)
        """
        # since we currently doesn't use multi-thread for each car, we can use heapq for better performance
        heap = []
        nodes = {}  # key: intersection, value: PathNode
        times = {}  # key: intersection, value: time

        sourceInter = source.getTarget()

        if destination.isIntersection():
            targetInter = destination.getIntersection()
        else:
            targetInter = destination.getRoad().getSource()

        sourceNode = PathNode(sourceInter)
        nodes[sourceInter] = sourceNode
        times[sourceInter] = 0
        heapq.heappush(heap, (0, sourceNode))

        while heap:
            time, currNode = heapq.heappop(heap)
            if currNode == targetInter:
                break
            timeAndNeighbor = self.realMap.neighborAndTime(currNode.intersection)
            for t, nextInter in timeAndNeighbor:
                newTime = t + time
                if nextInter in nodes:
                    if newTime < times[nextInter]:
                        heap.remove((times[nextInter], nodes[nextInter]))
                        heapq.heappush(heap, (newTime, nodes[nextInter]))
                        times[nextInter] = newTime
                        nodes[nextInter].backPtr = currNode
                else:
                    nodes[nextInter] = PathNode(nextInter)
                    nodes[nextInter].backPtr = currNode
                    times[nextInter] = newTime
                    heapq.heappush(heap, (newTime, nodes[nextInter]))


        # extract the entire path
        return self.extractPath(nodes[targetInter], sourceInter, car)

    def extractPath(self, node, source, car):
        """
        Extract the shortest path using the back pointer of each node starting
        from the target node to the source node. Store the extracted nodes reversely.

        :param targetNode: (PathNode) the target node
        :return: a list of path (roads)
        """
        roads = []

        while node and node.backPtr:
            preNode = node.backPtr
            found = False
            for road in preNode.intersection.getOutRoads():
                if road.getTarget() == node.intersection:
                    roads.insert(0, road)
                    found = True
                    break
            if found:
                node = node.backPtr
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
