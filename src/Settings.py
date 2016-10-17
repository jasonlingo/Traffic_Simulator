import sys

# ===============================================
# Traffic simulator settings
# ===============================================
EXP_NUM = 30000
"""The total number of learning trials"""

TAXI_NUM = 20
"""The initial number of taxis in the system"""

CAR_NUM = 500
"""The initial number of cars in the system"""

MAP_SIZE = 8000
"""Map size, the number of shape file record to be read"""

CALL_NEW_TAXI_TIME_GAP = 2
"""
The threshold of time (minute) for the system to call a new taxi that
might arrive the goal location with shorter time.
"""

SHAPEFILE = "/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf"
"""The filename of the shapefile for the traffic simulator"""

SPEED_LIMIT_ON_CRASH = 10
"""The speed limit of roads where  a crash happens"""

MAJOR_ROAD_INIT_CAR_NUM_RATIO = 0.8
"""The percentage that the number of cars on the major roads initially"""

# = fixed crash car location ====================
CRASH_ROAD = "Road_150"
"""Road for the crash"""

CRASH_RELATIVE_POSITION = 0.5
"""Relative position of the road (0.2 - 0.8, leave some space for the car's body)"""


# ===============================================
# Q-learning settings
# ===============================================
# Reward for reaching the goal state
GOAL_REWARD = 1000

# The time lapse (millisecond) for each move. #TODO: check the unit
TIME_STEP = 100

# The exploration factor
EPSILON = 0.15

# The minimal epsilon
MIN_EPSILON = 0.01

# The learning rate
ALPHA = 0.2

# The discounting factor
GAMMA = 0.8

# time threshold (seconds) for calling another taxi
CHECK_INTERVAL = 60

