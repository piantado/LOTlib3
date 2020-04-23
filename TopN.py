import heapq
from LOTlib3.Miscellaneous import Infinity

class QueueItem(object):
    """
            A wrapper to hold items and scores in the queue--just wraps "cmp" on a priority value
    """
    def __init__(self, item, p):
        self.item = item
        self.priority = p

    # def __cmp__(self, y):
    #     Comparisons are based on priority
        # return cmp(self.priority, y.priority)

    def __lt__(self, y):
        return self.priority < y.priority

class TopN(object):
    """
            This class stores the top N (possibly infinite) hypotheses it observes, keeping only unique ones.
            It works by storing a priority queue (in the opposite order), and popping off the worst as we need to add more
    """

    def __init__(self, N=Infinity, key='posterior_score'):
        assert N > 0, "*** TopN must have N>0"
        self.N = N
        self.key = key

        self.Q = [] # we use heapq to
        self.unique_set = set()

    def __contains__(self, y):
        return (y in self.unique_set)

    def __iter__(self):
        yield from self.get_all(sorted=True)

    def __len__(self):
        return len(self.Q)

    def add(self, x, p=None):
        # print [h for h in self]

        if p is None:
            p = getattr(x, self.key)

        # Add if we are too short or our priority is better than the *worst*
        # AND we aren't in the set
        if (len(self.Q) < self.N or p > self.Q[0].priority) \
           and x not in self.unique_set:

            l = len(self.Q)
            assert l <= self.N

            heapq.heappush(self.Q, QueueItem(x,p))
            self.unique_set.add(x)

            # And fix our size
            if len(self.Q) > self.N:
                y = heapq.heappop(self.Q)
                self.unique_set.remove(y.item)
                assert len(self.Q) == self.N

    def __lshift__(self, x):
        """ Just some friendlier notation """
        self.add(x)

    def get_all(self, **kwargs):
        """ Return all elements (arbitrary order). Does NOT return a copy. This uses kwargs so that we can call one 'sorted' """
        if kwargs.get('sorted', False):
            return [ c.item for c in sorted(self.Q, reverse=kwargs.get('decreasing',False))]
        else:
            return [ c.item for c in self.Q]

    def update(self, y):
        for yi in y:
            self.add(yi)

    def pop(self):
        v = heapq.heappop(self.Q).item
        self.unique_set.remove(v)
        self.N -= 1
        return v

    def best(self):
        return self.get_all(sorted=True)[-1]

if __name__ == "__main__":

    import random

    # Check the max
    for i in range(100):
        Q = TopN(N=10)

        ar = list(range(-100, 100))
        random.shuffle(ar)
        for x in ar: Q.add(x,x)

        assert set(Q.get_all()).issuperset( set([90,91,92,93,94,95,96,97,98,99]))

    print("Passed!")