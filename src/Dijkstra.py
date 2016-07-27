from Queue import PriorityQueue
import sys


def dijkstraSearch(graph, start, goals):
    """
    The dijkstra search algorithm for the taxi dispatching system. It expands routes from the start point until
    it reaches a goal's location.
    :param graph: a realMap object
    :param start: a starting point (in this system, this should be an intersection)
    :param goals: a list of taxis
    :return: the nearest taxi
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    cameFrom = {}
    costSoFar = {}
    cameFrom[start] = None
    costSoFar[start] = 0
    foundTaxi = {}
    fastestTaxi = None
    shortestTime = sys.maxint

    while not frontier.empty():
        current = frontier.get()
        # if costSoFar[current] > shortestTime:
        #     break

        # if current == goal:
        source = cameFrom[current]
        if source and current:
            roads = graph.getRoadsBetweenIntersections(source, current)
            cars = []
            for road in roads:
                for lane in road.lanes:
                    cars.extend([car for car in lane.getCars() if car and car.isTaxi])
            for car in cars:
                if car in goals:
                    if costSoFar[current] < foundTaxi.get(car.id, sys.maxint):
                        foundTaxi[car.id] = costSoFar[current]
                        if costSoFar[current] < shortestTime:
                            shortestTime = costSoFar[current]
                            fastestTaxi = car

        for next in graph.neighbors(current):
            new_cost = costSoFar[current] + graph.cost(current, next)
            if new_cost < costSoFar.get(next, sys.maxint):
                costSoFar[next] = new_cost
                frontier.put(next, new_cost)
                cameFrom[next] = current

    return (fastestTaxi, shortestTime) if fastestTaxi else (None, sys.maxint)


def dijkstraTrafficTime(graph, start, goals):
    """
    The dijkstra search algorithm for computing the shortest traffic time from the start to the goal location.
    :param graph: a realMap object
    :param start: a starting point (in this system, this should be an intersection)
    :param goals: a list of intersection
    :return: the shortest traffic time (in second)
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    cameFrom = {}
    costSoFar = {}
    cameFrom[start] = None
    costSoFar[start] = 0

    while not frontier.empty():
        current = frontier.get()
        if current in goals:  # FIXME: add lane position
            return costSoFar[current]
            break

        for next in graph.neighbors(current):
            new_cost = costSoFar[current] + graph.cost(current, next)
            if new_cost < costSoFar.get(next, sys.maxint):
                costSoFar[next] = new_cost
                frontier.put(next, new_cost)
                cameFrom[next] = current

    return sys.maxint

# def reconstructPath(came_from, start, goal):
#     current = goal
#     path = [current]
#     while current != start:
#         current = came_from[current]
#         path.append(current)
#     path.reverse()
#     return path