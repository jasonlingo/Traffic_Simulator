

class Destination(object):
    """
    A class that represents the destination of a car. The destination can be
    a intersection or a road position.
    """

    def __init__(self, inter=None, road=None, position=0):
        self.inter = inter
        self.road = road
        self.position = position

    def isIntersection(self):
        return self.inter is None

    def getIntersectoin(self):
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
