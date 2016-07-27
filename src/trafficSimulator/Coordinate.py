


class Coordinate(object):
    """
    A class that represent the coordinates of a point.
    """

    def __init__(self, lng, lat):
        self.lng = lng
        self.lat = lat

    def getCoords(self):
        return self.lng, self.lat

    def setCoord(self, lng, lat):
        self.lng = lng
        self.lat = lat
