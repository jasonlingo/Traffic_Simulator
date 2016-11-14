import heapq


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
        if item in self.items:
            self.removeItemFromQueue(item)
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

    def peek(self):
        if self.heap:
            return self.heap[0]
