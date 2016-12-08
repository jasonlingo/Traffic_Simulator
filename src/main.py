import threading
import matplotlib.pyplot as plt

from environment import Environment
from settings import SHAPEFILE
from settings import TAXI_NUM
from settings import CAR_NUM
from settings import MAP_SIZE
from settings import CRASH_RELATIVE_POSITION
from settings import CRASH_ROAD
from settings import MAJOR_ROAD_INIT_CAR_NUM_RATIO
from settings import NUM_TOP_TAXIS_TO_CRASH
from settings import RANDOM_SEED
from settings import UPDATE_NAVIGATION
from settings import PLOT_MAP
from trafficSimulator.config import POI_LAMBDA
from trafficSimulator.config import AVG_TIME_PERIOD
from trafficSimulator.realMap import RealMap
from trafficSimulator.animatedMap import AnimatedMap
from trafficController import TrafficController


def printParam():
    print "####################"
    print "Random seed = %d" % RANDOM_SEED
    print "Update_navigation:", UPDATE_NAVIGATION
    print "Time for average speed:", AVG_TIME_PERIOD
    print "Poisson lambda:", POI_LAMBDA
    print "####################"

if __name__ == '__main__':
    printParam()

    # Create a RealMap object and pass it to a Environment object.
    realMap = RealMap(SHAPEFILE, MAP_SIZE)
    env = Environment(realMap)
    carNum = CAR_NUM

    if CRASH_ROAD:
        # When CRASH_ROAD is not None, then the system want to use use a fixed crash location.
        # So keep one car for the crash.
        carNum -= 1

    # create a traffic controller
    trafficCtrl = TrafficController(
        env,
        carNum,
        TAXI_NUM,
        MAJOR_ROAD_INIT_CAR_NUM_RATIO,
        CRASH_ROAD,
        CRASH_RELATIVE_POSITION,
        NUM_TOP_TAXIS_TO_CRASH
    )

    # start simulation
    if PLOT_MAP:
        # Traffic simulator thread
        simulation = threading.Thread(target=trafficCtrl.run)
        simulation.start()

        # Plot the animated map
        fig, ax = plt.subplots(figsize=(14, 4))
        fig.set_dpi(85)  # adjust the subplot size
        ax.set_aspect(2.0)
        aniMap = AnimatedMap(realMap, env)
        aniMap.plotAnimatedMap(fig, ax)
    else:
        trafficCtrl.run()

    print "##### Experiments end #####"
