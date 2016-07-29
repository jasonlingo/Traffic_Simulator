import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from LanePosition import LanePosition
import sys


class Trajectory(object):
    """
    A class that represents the trajectory of a car.
    """

    def __init__(self, car, lane, position=0):
        """
        :param car:
        :param lane:
        :param position: the distance from the source to the car's locaiton
        :return:
        """
        self.car = car
        self.current = LanePosition(self.car, lane, position)
        self.current.acquire()

        # self.next = LanePosition(self.car, lane, position)
        self.next = LanePosition(self.car)
        # self.temp = LanePosition(self.car, lane, position)
        # self.temp = LanePosition(self.car)

        self.isChangingLanes = False
        self.absolutePosition = None
        # self.relativePosition = None

    def setGoal(self):
        self.current.setGoal()

    def isGoal(self):
        return self.current.isGoal()

    def getLane(self):
        # if self.temp.lane:
        #     return self.temp.lane
        # else:
        return self.current.lane

    def getRoad(self):
        return self.current.lane.road

    def getOppositeRoad(self):
        source = self.current.lane.road.getSource()
        sourceCoords = source.center.getCoords()
        target = self.current.lane.road.getTarget()
        for road in target.getOutRoads():
            if road.target.center.getCoords() == sourceCoords:
                return road

    def getAbsolutePosition(self):
        # if self.temp.lane:
        #     return self.temp.position
        # else:
        return self.current.position
        # return self.current.position

    def getRelativePosition(self):
        # if self.temp.lane:
        #     return self.getAbsolutePosition() / self.temp.lane.length
        # else:
        return self.getAbsolutePosition() / self.current.lane.getLength()

        # return self.getAbsolutePosition() / (float(self.temp.lane.length) if self.temp.lane else float(self.current.lane.length)
        # return self.current.position

    # def getDirection(self):
    #     # if self.temp.lane:
    #     #     return self.temp.lane.getDirection(self.getRelativePosition())
    #     # else:
    #     return self.current.lane.getDirection(self.getRelativePosition())
    #     # return self.lane.getDirection(self.getRelativePosition())

    def getCoords(self):
        return self.current.lane.getPoint(self.getRelativePosition())

    def nextCarDistance(self):
        curCar, curDist = self.current.nextCarDistance()
        nextCar, nextDist = self.next.nextCarDistance()
        if curDist < nextDist:
            return curCar, curDist
        else:
            return nextCar, nextDist

    def distanceToStopLine(self):
        if not self.canEnterIntersection():
            return self.getDistanceToIntersection()
        return sys.maxint

    def nextIntersection(self):
        return self.current.lane.road.target

    def previousIntersection(self):
        return self.current.lane.road.getSource()

    def isValidTurn(self):
        nextLane = self.car.nextLane
        # sourceLane = self.current.lane
        if not nextLane:
            print "no road to enter"
            return False
        # turnNumber = sourceLane.getTurnDirection(nextLane)
        # if turnNumber == 3:
        #     print "no U-turns are allowed"
        #     return False
        # if turnNumber == 0 and not sourceLane.isLeftmost:
        #     print "no left turns from this lane"
        #     return False
        # if turnNumber == 2 and not sourceLane.isRightmost:
        #     print "no right turns from this lane"
        #     return False
        return True

    def canEnterIntersection(self):
        """
        Determine whether this car can go through the intersection by checking the traffic light of it.
        :return: true if the car can enter the intersection. Otherwise false.
        """
        nextLane = self.car.nextLane
        sourceLane = self.current.lane
        if not nextLane:
            return True
        intersection = self.nextIntersection()
        return intersection.controlSignals.canEnterIntersection(sourceLane, nextLane)

    def getDistanceToIntersection(self):
        """
        Because the current position of this car is the point at the middle of this car, the distance
        to the intersection is:
            the length of the lane - the current position - half of the length of the car
        Note: the distance of this move is already added to this car's position
        :return: the distance from this car's position to the center of the intersection
        """
        distance = self.current.lane.getLength() - self.current.position - (self.car.length / 2.0)
        if not self.isChangingLanes:
            return max(distance, 0)
        else:
            return sys.maxint

    def timeToMakeTurn(self, plannedStep=0):
        """
        If the planned step is larger than the distance from the car's position to the intersection,
        then it is the time to make a turn.
        :param plannedStep: the planned step for this move
        :return: True or False
        """
        return self.getDistanceToIntersection() <= plannedStep

    def moveForward(self, distance):
        """
        :param distance:
        """
        if distance < 0:
            return
        self.current.position += distance
        self.next.position += distance
        if self.timeToMakeTurn() and self.canEnterIntersection() and self.isValidTurn():
            if not self.car.alive:  # go to sink intersection
                self.car.release()
                self.car.delete = True

            self.startChangingLanes(self.car.popNextLane(), distance)

        # if self.temp.lane:
        #     tempRelativePosition = self.temp.position / self.temp.lane.length
        # else:
        #     tempRelativePosition = 0

        gap = 2.0 * self.car.length  # TODO: why need double the length of the car
        # if self.isChangingLanes and self.temp.position > gap and not self.current.free: #fixme
        if self.isChangingLanes and not self.current.free:
            self.current.release()

        if self.isChangingLanes and self.next.free:# and self.temp.position + gap > (self.temp.lane.length if self.temp.lane else 0):
            self.next.acquire()
        if self.isChangingLanes:  # and tempRelativePosition >= 1:
            self.finishChangingLanes()
        if self.current.lane and not self.isChangingLanes and not self.car.nextLane:
            self.car.pickNextLane()

    def changeLane(self, nextLane):
        print "car %d is changing lane" % self.car.id
        if self.isChangingLanes:
            print "already changing lane"
            return
        if nextLane is None:
            print "no next lane"
            return
        if nextLane == self.lane:
            print "next lane == current lane"
            return
        if self.lane.road != nextLane.road:
            print "not neighbouring lanes"
            return
        nextPosition = self.current.position + self.car.length
        if nextPosition >= self.current.lane.getLength():
            print "too late to change lane"
            return
        return self.startChangingLanes(nextLane, nextPosition)

    def switchLane(self, targetLane):
        """
        Switch to the neighbor lane.
        :param targetLane:
        """
        if self.isChangingLanes:
            print "already changing lane"
            return
        if targetLane is None:
            print "no target lane"
            return
        if self.current.lane.road != targetLane.road:
            print "not on the same road"
            return
        if targetLane.canSwitchLane(self.current.position, self.car.length):
            self.current.release()
            self.current.lane = targetLane
            self.current.acquire()



    # def getIntersectionLaneChangeCurve(self):
    #     return

    # def getAdjacentLaneChangeCurve(self):
    #     p1 = self.current.lane.getPoint(self.current.relativePosition())
    #     p2 = self.next.lane.getPoint(self.next.relativePosition())
    #     distance = p2.subtract(p1).length
    #     direction1 = self.current.lane.middleLine.vector.normalized.mult(distance * 0.3)
    #     control1 = p1.add(direction1)
    #     direction2 = self.next.lane.middleLine.vector.normalized.mult(distance * 0.3)
    #     control2 = p2.subtract(direction2)
    #     return Curve(p1, p2, control1, control2)

    # def getCurve(self):
    #     return self.getAdjacentLaneChangeCurve()

    def startChangingLanes(self, nextLane, distance):
        """
        Change to the nextLane.
        :param nextLane:
        :param distance:
        """
        if self.isChangingLanes:
            print "already changing lane"
        if nextLane is None:
            print "no next lane"
        self.isChangingLanes = True
        self.next.lane = nextLane
        nextLaneCar, nextLaneCarPosition = self.next.nextCarDistance()
        # if nextLaneCar is None, then the
        # nextLaneCarPosition = nextLaneCarPosition if nextLaneCar else self.next.lane.getLength()  # TODO: check if we still need this
        remainderDistance = max(self.current.position - self.current.lane.getLength(), 0)
        nextPosition = min(remainderDistance, nextLaneCarPosition)
        self.next.position = nextPosition

    def finishChangingLanes(self):
        if not self.isChangingLanes:
            print "no lane changing is going on"
        self.next.release()
        # self.temp.release()
        self.isChangingLanes = False
        self.current.lane = self.next.lane
        self.current.position = self.next.position
        self.next.lane = None
        self.next.position = 0
        # self.temp.lane = None
        # self.temp.position = 0
        self.current.acquire()
        # return self.current.lane

    def release(self):
        if self.current:
            self.current.release()
        if self.next:
            self.next.release()
