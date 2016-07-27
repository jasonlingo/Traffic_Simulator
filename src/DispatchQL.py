from QLearning import QLearning
import random
from Settings import CHECK_INTERVAL

class DispatchQL(QLearning):
    """
    A Q-learning algorithm for learning dispatching policy
    """

    def __init__(self, exp, environment):
        """
        Args:
            taxis      : all taxis on the environment
            environment: the environment for this Q learning to interact with
            qvalue     : Q-value table
            nsa        : the table records the times of each state that has been reached
            epsilon    : a exploration parameter
            alpha      : learning rate
            gamma      : discounting factor
        Returns:
        """
        self.exp = exp
        self.env = environment
        self.epsilon = self.exp.epsilon
        self.alpha = self.exp.alpha
        self.gamma = self.exp.gamma

        # Q value lookup dictionary
        # {((x, y), action): Q value}
        self.qvalue = {}

        # record the visited times for state-action
        self.nsa = {}

        # record data for one trial
        self.stateAction = {}
        self.trialTime = CHECK_INTERVAL
        self.stateCalledTaxi = {}
        self.lastStateAction = None
        self.currStateAction = None
        self.updateQvalueFlag = False
        self.goal = self.exp.getGoalLocation().current.lane.road.id

    def go(self, interval):
        """
        Perform learning procedure.
        action: a nearest taxi
        state: the taxis' position (by road id)
        :param interval: second
        """
        """
        when a new taxi is called, give a negative reward to the previous policy

        learning process:
            get the current state (position of taxis)
            choose the quickest taxi
            let taxi go

            keep the lastest called taxi and state
        """
        self.trialTime += interval
        curState = self.getState()   # TODO: change to the sample of the speed of all roads

        taxi = None
        if self.trialTime >= CHECK_INTERVAL:
            taxi = self.chooseAction(curState)
            action = taxi.trajectory.current.lane.road.id
            self.currStateAction = (curState, taxi)  # TODO: action should be the position of a taxi, not a specific taxi
            if taxi in self.exp.taxiList:
                self.exp.callTaxi(taxi)
            self.updateQvalueFlag = True
            self.trialTime = 0

        # let taxis and cars move
        for ql in self.exp.calledTaxiQL:
            ql.go(interval)
        for otherTaxi in self.exp.taxiList:
            otherTaxi.move(interval)


        if self.updateQvalueFlag and taxi:
            nextState = self.getState()
            self.updateQvalueFlag = False
            reward = self.getReward(nextState, taxi)
            # action = taxi.trajectory.current.lane.road.id
            self.learn(curState, action, reward, nextState)
            self.lastStateAction = self.currStateAction # FIXME: need this?

    def getState(self):
        """
        The state should include the available taxis' location and the goal's location.
        TODO: considering a long road, we should include the relative position of a taxi on a road.
        """
        return (self.goal, tuple(sorted([taxi.trajectory.current.lane.road.id for taxi in self.exp.allTaxis if taxi.isAvailable() or taxi.isCalled()])))

    def getActions(self):
        taxiMapping = {}
        for taxi in self.exp.allTaxis:
            taxiMapping[taxi.trajectory.current.lane.road.id] = taxi
        return taxiMapping

    def getReward(self, state, action):
        if self.env.isGoalReached():
            return 1000
        if action is None:
            return 1
        else:
            return -1

    def resetTrial(self):
        self.trialTime = 0
        self.stateAction = {}

    def learn(self, state1, action1, reward, state2):
        """
        Args:
            state1: (road)
            action1 (Road): action taken in state1
            reward: (float) reward received after taking action at state1
            state2: (road)
        """
        actions = self.getActions().keys()
        maxqnew = max([self.qvalue.get((state2, a), 0.0) for a in actions])
        self.updateQValue(state1, action1, reward, maxqnew)

    def updateQValue(self, state, action, reward, maxqnew):
        self.nsa[(state, action)] = self.nsa.get((state, action), 0) + 1
        oldv = self.qvalue.get((state, action), 0.0)
        self.qvalue[(state, action)] = oldv + self.alpha * (reward + self.gamma * maxqnew - oldv)
        # TODO: take the nsa into account when update q vaule

    def chooseAction(self, state):
        """
        1. Randomly choose an action (taxi) if the random variable is less than the
           epsilon.
        2. Choose the action that has the highest q value of the given state.
        3. Choose the quickest taxi.
        Args:
            pos: LanePosition
        Returns:
            a chosen action
        """
        if not self.exp.allTaxis:
            return

        if random.random() < self.epsilon:  # TODO: make epsilon decrease gradually
            # exploration
            taxi = random.choice(self.exp.allTaxis)
        else:
            taxiMapping = self.getActions()
            actions = taxiMapping.keys()
            q = [self.qvalue.get((state, a), 0.0) for a in actions]
            maxQIdx = q.index(max(q))
            action = actions[maxQIdx]
            taxi = taxiMapping[action]

            # TODO: why use following logic
            # if maxQIdx > 0:
            #     action = actions[maxQIdx]
            #     taxi = taxiMapping[action]
            # else:
            #     # taxi, trafficTime = self.exp.findFastestTaxi()
            #     taxi = random.choice(self.exp.allTaxis)

            if not self.exp.isQuicker(taxi, CHECK_INTERVAL):
                taxi = None
        return taxi

