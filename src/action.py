

class Action:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"

    @classmethod
    def getActions(cls):
        return [cls.NORTH, cls.SOUTH, cls.EAST, cls.WEST]