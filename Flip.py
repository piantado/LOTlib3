"""

In LOTlib expressions we may sometimes want to use a random flip. This makes the outcomes of evaluation stochastic. A simple
way to handle this is to use the Hypotheses.StochasticSimulation code, which will compute the distribution of outcomes
by simplying running the program forward many times.

The alternative is this code, which uses a special "random context" and "flip" which allows you to, up to a certain depth,
enumerate all of the possible program traces and their associated probabilities. Thisi is based on many ideas from
probabilistic programming.
"""
from math import log
from collections import defaultdict
from LOTlib3.Miscellaneous import logplusexp, lambdaMinusInfinity
import LOTlib3

class TooManyContextsException(Exception):
    """ Called when a ContextSet has too many contexts in it
    """
    pass

class ContextSizeException(Exception):
    pass


import heapq
class ContextSet(object):
    """ Store a set of contexts, only the top N """

    def __init__(self):
        self.Q = []

    def pop(self):
        return heapq.heappop(self.Q)

    def add(self, o):
        return heapq.heappush(self.Q, o)

    def __len__(self):
        return len(self.Q)

    def __str__(self):
        return "<Context set: %s>" % self.Q


class RandomContext(object): # manage uncertainty
    """
    This stores a list of random choices we have made, to allow us to evaluate a stochastic hypothesis in a deterministic way,
    by calling RandomContext.flip().

    """

    def __init__(self, cs, choices=(), lp=0.0, max_size=1024):
        self.choices = choices
        self.contextset = cs # who we update
        self.idx = 0
        self.lp = lp
        self.max_size = max_size

    def __str__(self):
        return "<RandomContext: %s>" % str(self.choices)
    def __repr__(self):
        return str(self)

    def __cmp__(self, other): # comparisons are made by lp. We do this way so that heapq stores the *highest* prob
        return self.lp < other.lp

    def flip(self, p=0.5):
        """ Flip a coin according to the context. This is somewhat complicated. If we have outcomes stored in the
        context, return the right one, accumulating the probability. If we don't have an outcome determined, then
        return default (True), and push the *other* outcome (and its whole context onto contextset, so that we
        visit that route later.

        This can be used in a grammar like
        C.flip(p=0.8)
        and then when we use the clases here we can enumerate all program traces

        """
        # print "Calling flip with context set ", self.contextset, self.idx, self.choices
        ret = None

        if self.idx < len(self.choices): # if we are on the specified choices
            ret = self.choices[self.idx]
            # print "\tFlip ret: ", ret
            assert ret is True or ret is False # must have this
        else:
            ret = True # which way we choose when its unspecified

            otherpath = RandomContext(self.contextset, choices=self.choices + (not ret,), lp=self.lp + log(1.0-p), max_size=self.max_size)

            # The choice we make later
            self.contextset.add(otherpath)

            # the choice we make now
            self.choices = self.choices + (ret,)
            self.lp += log(p)

            # this is necessary because otherwise we can hang
            if len(self.choices) > self.max_size:
                raise ContextSizeException

        self.idx += 1
        return ret

    def uniform_sample(self, outcomes):
        """ All possible outcomes """
        # print "Calling uniform sample with context set ", self.contextset, self.idx, self.choices
        ret = None

        if self.idx < len(self.choices):  # if we are on the specified choices
            ret = self.choices[self.idx]
            # print "\tUniform_sample ret: ", ret
        else:
            ret = outcomes[0]  # defaultly choose the first outcome

            thislp = -log(len(outcomes)) # the probability of each outcome

            for k in outcomes[1:]:

                otherpath = RandomContext(self.contextset, choices=self.choices + (k,), lp=self.lp + thislp,
                                          max_size=self.max_size)

                # The choice we make later
                self.contextset.add(otherpath)

            # the choice we make now
            self.choices = self.choices + (ret,)
            self.lp += thislp

            # this is necessary because otherwise we can hang
            if len(self.choices) > self.max_size:
                raise ContextSizeException

        self.idx += 1

        return ret


def compute_outcomes(f, *args, **kwargs):
    """
    Return a dictionary of outcomes using our RandomContext tools, giving each possible trace (up to the given depth)
    and its probability.
    f here is a function of context, as in f(context, *args)

    kwargs['Cfirst'] constrols whether C is the first or last argument to f. It cannot be anything else

    In kwargs you can pass "catchandpass" as a tuple of exceptions to catch and do nothing with
    """

    out = defaultdict(lambdaMinusInfinity)  # dict from strings to lps that we accumulate

    cs = ContextSet() # this is the "open" set of contexts we need to explore
    cs.add(RandomContext(cs)) # add a single context with no history

    i = 0
    while len(cs) > 0:
        context = cs.pop()  # pop an element from Context set.
        # print "CTX", context.lp, context#, "  \t", cs.Q

        try:
            # figure out the ordering of where C is passed to the lambda
            if kwargs.get('Cfirst', True):# does C go at the beginning or the end?
                v = f(context, *args) # when we call context.flip, we may update cs with new paths to explore
            else:
                newargs = args + (context,)
                v = f(*newargs)
            # print ">>>", v
            # add up the lp for this outcomem
            out[v] = logplusexp(out[v], context.lp)
        except kwargs.get('catchandpass', None) as e:
            pass
        except ContextSizeException: # prune that path
            pass

        if i >= kwargs.get('maxit', 1000):
            return out ## TODO: Hmm can either return the partial answer here or raise an exception

        if len(cs) > kwargs.get('maxcontext', 1000): # sometimes we can generate way too many contexts, so let's avoid that
            raise TooManyContextsException

        i += 1

    return out