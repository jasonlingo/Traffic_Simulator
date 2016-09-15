from Environment import Environment
from Experiment import Experiment
from Settings import EXP_NUM, SHAPEFILE, TAXI_NUM, CAR_NUM, EPSILON, ALPHA, GAMMA
from trafficSimulator.RealMap import RealMap
from trafficSimulator.AnimatedMap import AnimatedMap
from TrafficController import TrafficController
import threading
import matplotlib.pyplot as plt


if __name__ == '__main__':

    DEBUG = False

    # def runExp():
    #     """
    #     Perform the learning thread for EXP_NUM trials.
    #     """
    #
    #     while not realMap.isAniMapPlotOk() and not DEBUG:
    #         # wait until the map has been plotted
    #         time.sleep(1)
    #
    #     for i in range(EXP_NUM):
    #         print "========== " + str(i + 1) + "-th trial =========="
    #         print "Goal locates at", exp.getGoalLocation().current.lane.road.id
    #         exp.startLearning()

        # Print the results ======
        # experiment.printQValue()
        # experiment.printNSA()
        # experiment.showMap()

    # Create a RealMap object and pass it to a Environment object.
    mapSize = 8000  # number of shapefile data to be read to construct the map
    realMap = RealMap(SHAPEFILE, mapSize)
    env = Environment(realMap)
    # exp = Experiment(env, TAXI_NUM, CAR_NUM, epsilon=EPSILON, alpha=ALPHA, gamma=GAMMA)
    initCarNum = 10
    initTaxiNum = 10
    trafficCtrl = TrafficController(env, initCarNum, initTaxiNum)

    # For debugging usage. If debugging mode is turned on, then it will not
    if DEBUG:
        # runExp()
        trafficCtrl.run()

    # Traffic simulator thread
    simulation = threading.Thread(target=trafficCtrl.run)
    simulation.start()

    # Plot the animated map
    fig, ax = plt.subplots(figsize=(14, 4))

    fig.set_dpi(85)  # adjust the subplot size
    ax.set_aspect(1.0)
    aniMap = AnimatedMap(realMap, env)
    aniMap.plotAnimatedMap(fig, ax)

    print "##### Experiments end #####"
