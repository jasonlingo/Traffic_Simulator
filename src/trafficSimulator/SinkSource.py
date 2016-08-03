

class SinkSource(object):
    """
    A class that represents the destination of a car. The destination can be
    a intersection or a road position.
    """

    def __init__(self, inter, road=None, position=0):
        """
        :param inter: Intersection object
        :param road: Road object
        :param position: relative position (0~1)
        """
        self.inter = inter
        self.road = road
        self.position = position

    def isIntersection(self):
        return self.inter is not None

    def getIntersection(self):
        return self.inter

    def getRoadPos(self):
        return self.road, self.position

    def isReached(self, lanePos):
        """
        Chech whether the given LanePosition has reached the destinatino.
        :param lanePos:
        :return: True if reached
        """
        if self.inter:
            nextInter = lanePos.getNextInter()
            return self.inter == nextInter
        else:
            road = lanePos.getRoad()
            return self.road == road and self.position <= lanePos.getPosition

    def getCoords(self):
        if self.inter is not None:
            return self.inter.center.getCoords()
        else:
            source = self.road.getSource().getCoords()
            target = self.road.getTarget().getCoords()
            lng = source[0] + (target[0] - source[0]) * self.position
            lat = source[1] + (target[1] - source[1]) * self.position
            return lng, lat

