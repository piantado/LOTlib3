"""

Versions of scheme that return dictionaries for all possible outcomes, where the outcomes are strings

Here, the probabilities that are stored in the dictionary are log probabilities
"""


from LOTlib3.Primitives import primitive
from collections import defaultdict
from LOTlib3.Miscellaneous import logplusexp, Infinity, nicelog, log1mexp, lambdaMinusInfinity

@primitive
def cons_d(x,y):
    out = defaultdict(lambdaMinusInfinity)

    for a, av in list(x.items()):
        for b, bv in list(y.items()):
            out[a+b] = logplusexp(out[a+b], av + bv)
    return out

@primitive
def cdr_d(x):
    out = defaultdict(lambdaMinusInfinity)
    for a, av in list(x.items()):
        v = a[1:] if len(a) > 1 else ''
        out[v] = logplusexp(out[v], av)
    return out


@primitive
def car_d(x):
    out = defaultdict(lambdaMinusInfinity)
    for a, av in list(x.items()):
        v = a[1] if len(a) > 1 else ''
        out[v] = logplusexp(out[v], av)
    return out

@primitive
def flip_d(p):
    return {True: nicelog(p), False: nicelog(1.-p)}

@primitive
def empty_d(x):
    p = x.get('', -Infinity)
    return {True: p, False:log1mexp(p)}

@primitive
def if_d(prb,x,y):
    out = defaultdict(lambdaMinusInfinity)
    pt = prb[True]
    pf = prb[False]
    for a, av in list(x.items()):
        out[a] = av + pt
    for b, bv in list(y.items()):
        out[b] = logplusexp(out[b], bv + pf)

    return out

@primitive
def equal_d(x,y):
    peq = -Infinity
    for a,v in list(x.items()):
        peq = logplusexp(peq, v + y.get(a,-Infinity)) # P(x=a,y=a)
    return {True: peq, False:log1mexp(peq)}

@primitive
def and_d(x,y):
    out = defaultdict(lambdaMinusInfinity)
    out[True] = x.get(True,-Infinity) + y.get(True,-Infinity)
    out[False] = log1mexp(out[True])
    return out

@primitive
def or_d(x,y):
    out = defaultdict(lambdaMinusInfinity)
    out[True] = logplusexp(x.get(True,-Infinity) + y.get(False,-Infinity),
                           x.get(False,-Infinity) + y.get(True,-Infinity))
    out[False] = log1mexp(out[True])
    return out

@primitive
def not_d(x):
    out = defaultdict(lambdaMinusInfinity)
    out[True] = x.get(False,-Infinity)
    out[False] = log1mexp(out[True])
    return out

@primitive
def sample_uniform_d(s):
    """ return a unifom sample of the set s """
    l = -nicelog(len(s))
    return {x: l for x in s }