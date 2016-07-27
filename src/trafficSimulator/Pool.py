


class Pool(object):

    def __init__(self, factory, pool):
        self.objects = {}
        self.factory = factory

        if pool is not None and pool.objects is not None:
            for k in pool.objects:
                self.objects[k] = self.factory.copy(pool.objects[k])

    def length(self):
        return len(self.objects)

    def get(self, id):
        return self.objects[id]

    def put(self, obj):
        self.objects[obj.id] = obj

    def pop(self, obj):
        if obj.id:
            id = obj.id
        else:
            id = obj
        result = self.objects[id]
        if result.release == "function":
            result.release()
        del self.objects[id]
        return result

    def all(self):
        return self.objects

    def clear(self):
        self.objects = {}
        return self.objects



