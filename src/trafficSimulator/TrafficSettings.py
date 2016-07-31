# ===============================================
# Settings
# ===============================================
METER_TYPE = "K"
"""Use kilometer (K) or mile (M) for the haversine function"""

EARTH_RADIUS_MILE = 3959.0
"""The radius of the earth in miles"""

EARTH_RADIUS_KM = 6371.0
"""The radius of the earth in kilometers"""

GRID_SIZE = 32
DEFAULT_TIME_FACTOR = 5
LIGHT_FLIP_INTERVAL = 10
CARS_NUMBER = 100
TAXI_NUMBER = 20
SHAPEFILE_NAME = "/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf"
MAX_SPEED = 60.0

MAX_ROAD_LANE_NUM = 2
"""Maximum number of lanes per road"""

CLOSE_CRASH_LANE = False
"""block the lane where a crash happens"""

CLOSE_ALL_CRASH_LANES = False
"""block all the lanes of a road that a crash happens"""

ANIMATION_LAPSE = 100
"""The interval (millisecond) between two animation frame"""

CAR_LENGTH = 0.0045
"""The length (in km) of a car"""

POI_LAMBDA = 0.01
"""lambda parameter for poisson arrival for the new car comes into the map"""
