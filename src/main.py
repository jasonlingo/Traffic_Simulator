from Environment import Environment
from Settings import SHAPEFILE, TAXI_NUM, CAR_NUM, MAP_SIZE, EPSILON, ALPHA, GAMMA
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
    realMap = RealMap(SHAPEFILE, MAP_SIZE)
    env = Environment(realMap)
    # exp = Experiment(env, TAXI_NUM, CAR_NUM, epsilon=EPSILON, alpha=ALPHA, gamma=GAMMA)
    trafficCtrl = TrafficController(env, CAR_NUM, TAXI_NUM)

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
    ax.set_aspect(2.0)
    aniMap = AnimatedMap(realMap, env)
    aniMap.plotAnimatedMap(fig, ax)

    print "##### Experiments end #####"
