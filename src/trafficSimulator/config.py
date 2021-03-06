import sys

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

MAP_TYPE = "satellite"
"""map type: roadmap / satellite / terrain / hybrid"""

# ============================================================================
# map settings
# # ============================================================================
METER_TYPE = "KM"
"""Use kilometer (KM) or mile (MILE) for the haversine function"""

# EARTH_RADIUS_MILE = 3959.0
# """The radius of the earth in miles"""
#
# EARTH_RADIUS_KM = 6371.0
# """The radius of the earth in kilometers"""

# GRID_SIZE = 32
# DEFAULT_TIME_FACTOR = 5

LIGHT_FLIP_INTERVAL = 15
"""The time interval for the traffic light to change its signals"""

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

POI_LAMBDA = 0.00002
"""The lambda parameter for poisson arrival for a new car comes into the map"""

UPDATE_ROUTE_TIME = 30
"""The time (seconds) for updating navigation"""

MAJOR_ROAD_MIN_LEN = 0.2
"""The minimum length (in km) for a major roads. If a road is longer than this length, it is a major road."""

MAJOR_ROAD_POI_LAMBDA = POI_LAMBDA * 3
"""The lambda parameter for poisson arrival for a new car comes into the map"""

AVG_TIME_PERIOD = 300
"""Time period (in second) for calculating average drive time of a road"""

PERCENTAGE_FOR_AVG_DRIVE_TIME = 0.4
"""The percentage of"""

# probabilities for edge intersections to be a sink or source places
SINK_PROB = 0.15
SOURCE_PROB = 0.15
SINK_SOURCE_PROB = 0.2

# minimal road length (km) for a sink or source point
MIN_SINK_SOURCE_ROAD_LENGTH = 0.2
ROAD_OFFSET_FOR_SINK_SOURCE_POINT = 0.1

# ============================================================================
# Animation MAP Configuration
# ============================================================================
# multiple for the car's size
CAR_LEN_MULTI = 16000

# (r, g, b)
MAP_COLOR = {"myYellow": (1, 1, 0.3),
          "calledTaxi": (1, 0, 1),
          "majorRoad": (0/255, 1, 115/255),
          "path": (0, 1, 1)}