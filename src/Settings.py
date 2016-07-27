
# ===============================================
# Traffic simulator settings
# ===============================================
# The total number of learning trials
EXP_NUM = 30000

# The total number of taxis in the system
TAXI_NUM = 20

# The total number of cars in the system
CAR_NUM = 20

# The threshold of time (minute) for the system to call a new taxi that
# might arrive the goal location with shorter time.
CALL_NEW_TAXI_TIME_GAP = 2

# The filename of the shapefile for the traffic simulator
SHAPEFILE = "/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf"


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


# ===============================================
# Discarded settings
# ===============================================
# ENV_BOTTOM = 0                                         # the bottom limit of the experiment region
# ENV_TOP = 50                                           # the top limit of the experiment region
# ENV_LEFT = 0                                           # the left limit of the experiment region
# ENV_RIGHT = 50                                         # the right limit of the experiment region
# SUB_REGION_NUM = max(ENV_TOP * ENV_RIGHT / 50, 1)      # the number of sub-regions in the map
# MAX_SUB_REGION_SIDE = min(ENV_TOP, ENV_RIGHT) / 5      # the maximum length of side for sub-region
# DELETE_ROAD_NUM = ENV_TOP * ENV_RIGHT / 4              # determine the road density