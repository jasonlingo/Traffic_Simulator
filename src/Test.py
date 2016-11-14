# import heapq
#
# class Weight(object):
#
#     def __init__(self, pri, name):
#         self.pri = pri
#         self.name = name
#
#     def __cmp__(self, other):
#         return cmp(self.pri, other.pri)
#
#
# A = Weight(10, "A")
# B = Weight(5, "B")
# C = Weight(10.111, "C")
# D = Weight(0.1, "D")
#
# queue = []
# heapq.heappush(queue, A)
# heapq.heappush(queue, B)
# heapq.heappush(queue, D)
# heapq.heappush(queue, C)
#
# queue.remove(C)
# heapq.heapify(queue)
#
#
#
# while queue:
#     curt = heapq.heappop(queue)
#     print curt.name
#
#
