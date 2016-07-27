

class Segment(object):


    def __init__(self, source, target):
        self.source = source
        self.target = target
        self._vector = None

    def vector(self):
        self._vector = self.target.subtract(self.source)
        return self._vector

    def length(self):
        return self._vector.length

    def direction(self):
        return self._vector.direction

    def center(self):
        return self.getPoint(0.5)

    def split(self, n, reverse):
        # order = None
        if reverse:
            if n - 1 <= 0:
                order = [i for i in range(n-1, 1)]  # n-1, n, n+1, ..., 0
            else:
                order = [i for i in range(n-1, -1, -1)]  # n-1, n-2, ..., 0
        else:
            if 0 <= n - 1:
                order = [i for i in range(n)]  # 0, 1, ..., n-1
            else:
                order = [i for i in range(0, n, -1)]  # 0, -1, ..., n-1
        result = []
        for i in range(len(order)):
            k = order[i]
            result.append(self.subsegment(k / float(n), (k+1) / float(n)))
            
    def getPoint(self, a):
        result = self.source.add(self.vector().mult(a))
        return result  # FIXME: check the return of self.source.add()

    def subsegment(self, a, b):
        offset = self.vector()
        start = self.source.add(offset.mult(a))
        end = self.source.add(offset.mult(b))
        return Segment(start, end)
