import sys
import heapq

from collections import defaultdict
from fixedRandom import FixedRandom


class Traffic(object):

    # time for the entire simulator
    globalTime = 0.0
    globalTimeLimit = sys.float_info.max

    SECOND_PER_HOUR = 3600.0

    carIsCrashed = False

    uniqueid = defaultdict(int)

    @classmethod
    def uniqueId(cls, idType):
        cls.uniqueid[idType] += 1
        return idType + "_" + str(cls.uniqueid[idType])

    @classmethod
    def increaseGlobalTime(cls, deltaTime):
        if Traffic.globalTimeLimit - deltaTime < Traffic.globalTime:  # prevent overflow
            Traffic.globalTime = deltaTime - (Traffic.globalTimeLimit - Traffic.globalTime)
        else:
            Traffic.globalTime += deltaTime


class RoadType(object):
    ROAD = "Road"
    INTERSECTION = "Intersection"


class CarType(object):
    CAR = "car"
    TAXI = "taxi"


class RouteWeight(object):  # TODO: replace this by PriorityItem

    def __init__(self, time, intersection):
        self.time = time
        self.intersection = intersection

    def __cmp__(self, other):
        return cmp(self.time, other.time)


class PriorityItem(object):

    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


class PriorityItemQueue(object):

    def __init__(self):
        self.heap = []
        self.items = {}

    def push(self, priority, item):
        newPriorityItem = PriorityItem(priority, item)
        self.items[item] = newPriorityItem
        heapq.heappush(self.heap, newPriorityItem)

    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)

    def removeItemFromQueue(self, item):
        if item in self.items:
            priorityItem = self.items[item]
            if priorityItem in self.heap:
                self.heap.remove(priorityItem)
                heapq.heapify(self.heap)
            del self.items[item]

    def peek(self):
        if self.heap:
            return self.heap[0]

    def size(self):
        return len(self.heap)

    def containsItem(self, item):
        return item in self.items

    def getItemPriority(self, item):
        if self.containsItem(item):
            return self.items[item].priority



def sampleOne(list):
    """
    randomly pick one element from the given list.
    :param list:
    :return: a randomly picked item
    """
    return FixedRandom.sample(list, 1)[0]
