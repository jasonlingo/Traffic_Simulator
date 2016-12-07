from __future__ import print_function
import sys


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
