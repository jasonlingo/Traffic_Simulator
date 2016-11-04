from Environment import Environment
from Settings import SHAPEFILE
from Settings import TAXI_NUM
from Settings import CAR_NUM
from Settings import MAP_SIZE
from Settings import CRASH_RELATIVE_POSITION
from Settings import CRASH_ROAD
from Settings import MAJOR_ROAD_INIT_CAR_NUM_RATIO
from Settings import NUM_TOP_TAXIS_TO_CRASH
from trafficSimulator.RealMap import RealMap
from trafficSimulator.AnimatedMap import AnimatedMap
from TrafficController import TrafficController
import threading
import matplotlib.pyplot as plt


if __name__ == '__main__':

    DEBUG = True

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
    carNum = CAR_NUM
    if CRASH_ROAD:
        carNum -= 1
    trafficCtrl = TrafficController(env,
                                    carNum,
                                    TAXI_NUM,
                                    MAJOR_ROAD_INIT_CAR_NUM_RATIO,
                                    CRASH_ROAD,
                                    CRASH_RELATIVE_POSITION,
                                    NUM_TOP_TAXIS_TO_CRASH)

    # For debugging usage. If debugging mode is turned on, then it will not
    if DEBUG:
        # runExp()
        trafficCtrl.run()
    else:
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
