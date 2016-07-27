from __future__ import print_function
import sys


class PriorityQueue(object):
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """
    def  __init__(self):
        self.heap = {}
        self.count = 0

    def push(self, item, priority):
        if priority in self.heap:
            self.heap[priority].append(item)
        else:
            self.heap[priority] = [item]
        self.count += 1

    def pop(self):
        """
        Pop the item with the smallest key value.
        Returns: item
        """
        key = min(self.heap.keys())
        item = self.heap[key].pop(0)
        if len(self.heap[key]) == 0:
            self.heap.pop(key)
        self.count -= 1
        return item

    def update(self, item, oldKey, newKey):
        queue = self.heap[oldKey]
        queue.remove(item)
        if not queue:
            self.heap.pop(oldKey)
        self.count -= 1
        self.push(item, newKey)

    def isEmpty(self):
        return self.count == 0

    def printQueue(self):
        for key in sorted(self.heap.keys()):
            print (key,": ", self.heap[key])


def BFS(map, source, dest):
    source, _ = map.findRoad(source)
    dist = {}
    for x in range(map.sizeX):
        for y in range(map.sizeY):
            if map.road[x][y]:
                dist[(x, y)] = sys.maxint

    queue = []
    dist[source] = 0
    queue.append(source)

    while queue:
        u = queue.pop(0)

        for n in adjacent(map, u):
            if dist[n] == sys.maxint:
                dist[n] = dist[u] + 1
                if n == dest:
                    return dist[n]
                queue.append(n)

def adjacent(map, pos):
    adj = []
    if map.checkRoadPoint(pos[0], pos[1]+1):
        adj.append((pos[0], pos[1]+1))
    if map.checkRoadPoint(pos[0], pos[1]-1):
        adj.append((pos[0], pos[1]-1))
    if map.checkRoadPoint(pos[0]+1, pos[1]):
        adj.append((pos[0]+1, pos[1]))
    if map.checkRoadPoint(pos[0]-1, pos[1]):
        adj.append((pos[0]-1, pos[1]))
    return adj

