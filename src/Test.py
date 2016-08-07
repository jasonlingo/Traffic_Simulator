import heapq

heap = []
heapq.heappush(heap, (2, "a"))
heapq.heappush(heap, (4, "b"))
heapq.heappush(heap, (1, "c"))

# heap.remove((2, "a"))

while heap:
    print heap
    if (2, "a") in heap:
        heap.remove((2, "a"))
    print heapq.heappop(heap)