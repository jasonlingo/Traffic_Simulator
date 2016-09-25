# ============================================================================
# Google API and background map
# ============================================================================
GOOGLE_STATIC_MAP_KEY = "AIzaSyBi3aJFeFLJ14VtWv2ERQ9R-BAbIxjOjyA"
"""The API key for Google static map"""

GOOGLE_STATIC_MAP_API_ADDRESS = "https://maps.googleapis.com/maps/api/staticmap?"
"""The API address for Google static map"""

MAP_FOLDER = "/trafficSimulator/pic/map"
"""The folder for storing google map image file"""

BG_MAP_NAME = "bg_map.jpg"
"""The background map's file name"""

RESIZED_MAP_NAME = "resized_map.png"
"""The resized background map's file name"""

# ============================================================================
# map settings
# ============================================================================
METER_TYPE = "K"
"""Use kilometer (K) or mile (M) for the haversine function"""

EARTH_RADIUS_MILE = 3959.0
"""The radius of the earth in miles"""

EARTH_RADIUS_KM = 6371.0
"""The radius of the earth in kilometers"""

# GRID_SIZE = 32
# DEFAULT_TIME_FACTOR = 5

LIGHT_FLIP_INTERVAL = 10
"""The time interval """

# SHAPEFILE_NAME = "/Users/Jason/GitHub/Research/QLearning/Data/Roads_All.dbf"

MAX_SPEED = 60.0
"""The default speed limit for roads"""

MAX_ROAD_LANE_NUM = 2
"""Maximum number of lanes per road"""

CLOSE_CRASH_LANE = False
"""block the lane where a crash happens"""

CLOSE_ALL_CRASH_LANES = False
"""block all the lanes of a road that a crash happens"""

ANIMATION_LAPSE = 100
"""The interval (millisecond) between two frames"""

CAR_LENGTH = 0.0045
"""The length (in km) of a car"""

CAR_WIDTH = 0.0018
"""The width (in km) of a car"""

POI_LAMBDA = 0.00005
"""lambda parameter for poisson arrival for the new car comes into the map"""


