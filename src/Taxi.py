from FixedRandom import FixedRandom


class Taxi:

    def __init__(self, id, x, y, speed=1):
        """
        :param id: the taxi's id
        :param x: the x coordinate of this taxi
        :param y: the y coordinate of this taxi
        :param speed: the speed of this taxi
        :return:
        """
        self.id = id
        self.x, self.y = x, y
        self.speed = speed
        self.available = True
        self.called = False
        self.destination = None
        # keep track of the route
        self.randomRouteX = [x]
        self.randomRouteY = [y]
        self.toGoalRouteX = []
        self.toGoalRouteY = []

    def setRandomAvailable(self, changeProb=0.8):
        """
        Args:
            changeProb: the probability of change availability status
        """
        if FixedRandom.random() >= changeProb:
            self.available = not self.available

    def getPosition(self):
        return self.x, self.y

    def setPosition(self, pos):
        (self.x, self.y) = pos
        if self.called:
            self.toGoalRouteX.append(pos[0])
            self.toGoalRouteY.append(pos[1])
        else:
            self.randomRouteX.append(pos[0])
            self.randomRouteY.append(pos[1])

    def isCalled(self):
        return self.called

    def beenCalled(self):
        self.called = True
        self.available = True

    def equals(self, taxi):
        return self.id == taxi.getId()

    def getId(self):
        return self.id

    def goRandomly(self, env):
        actions = env.getAction(self.getPosition())
        if actions is not None:
            action = FixedRandom.choice(actions)
            self.setPosition(env.nextPos(self, action))
