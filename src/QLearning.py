from collections import Counter
import random


class QLearning(object):
    """
    A Q-learning model.
    """

    def __init__(self, taxi, environment, qvalue={}, nsa={}, epsilon=0.1, alpha=0.1, gamma=0.9):
        """
        Args:
            taxi: the assigned taxi
            environment: the environment for this Q learning to interact with
            qvalue: Q-value table
            nsa: the table records the times of each state that has been reached
            epsilon: a exploration parameter
            alpha: learning rate
            gamma: discounting factor
        Returns:
        """
        self.taxi = taxi
        self.env = environment
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = qvalue

        # record the visited times for state-action
        self.nsa = nsa

        # for checking oscillation
        self.steps = {}

    def go(self, second):
        """
        Perform learning procedure.
        """
        oldPos = self.taxi.getPosition().lane.road

        # already at the same road with the goal location
        if self.env.checkArriveGoal(oldPos): # TODO: not only has to be at the same road, but also need to be close to the crash's location
            self.env.setReachGoal(True)
            reward = self.env.getReward(oldPos, oldPos)
            self.learn(oldPos, oldPos, reward, oldPos)
            return

        action = self.chooseAction(oldPos)  # road
        nextLane = action.getFastestLane()
        self.taxi.setNextLane(nextLane)
        self.taxi.move(second)
        nextPos = self.taxi.getPosition().lane.road  # current road

        if oldPos != nextPos:
            reward = self.env.getReward(nextPos, action)
            self.learn(oldPos, action, reward, nextPos)

            self.steps[nextPos] = self.steps.get(nextPos, 0) + 1
            if self.steps[nextPos] > 1000:
                print "Oscillation at: ", nextPos, " => ", self.steps[nextPos]

        if self.env.checkArriveGoal(nextPos):
            self.env.setReachGoal(True)

    def learn(self, state1, action1, reward, state2):
        """
        Args:
            state1: (road)
            action1 (Road): action taken in state1
            reward: (float) reward received after taking action at state1
            state2: (road)
        Returns:
        """
        actions = self.env.getAction(state2)
        maxqnew = max([self.qvalue.get((state2, a), 0.0) for a in actions])
        self.updateQValue(state1, action1, reward, maxqnew)

    def updateQValue(self, state, action, reward, maxqnew):
        self.nsa[(state, action)] = self.nsa.get((state, action), 0) + 1
        oldv = self.qvalue.get((state, action), 0.0)
        self.qvalue[(state, action)] = oldv + self.alpha * (reward + self.gamma * maxqnew - oldv)
        # TODO: take the nsa into account when update q value

    def chooseAction(self, state):
        """
        Randomly choose an action if the random variable is less than the
        epsilon. Or choose the action that has the highest q value of the
        given state.
        Args:
            pos: LanePosition
        Returns:
            a chosen action
        """
        actions = self.env.getAction(state)  # roads

        if random.random() < self.epsilon:
            action = random.choice(actions)  # exploration
        else:
            q = [self.qvalue.get((state, a), 0.0) for a in actions]
            if len(Counter(q)) == 1 and 0.0 in q:
                # when all actions have not been taken before
                action = random.choice(actions)
            else:
                maxQIdx = q.index(max(q))
                action = actions[maxQIdx]
        return action

    def getTaxi(self):
        return self.taxi
