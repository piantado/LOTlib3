from LOTlib3.Eval import primitive
from LOTlib3.Miscellaneous import flip, Infinity
import numpy

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Stochastic Primitives
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@primitive
def flip_(p=0.5):
    return flip(p)

@primitive
def binomial_(n, p):
    if 0 < n < Infinity and 0. <= p <= 1 and (isinstance(n, int) or n.is_integer()):
        return numpy.random.binomial(int(n), p)
    else:
        return float("nan")