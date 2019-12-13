from LOTlib3.Eval import primitive
from LOTlib3.Miscellaneous import Infinity
from math import isnan, isinf

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set-theoretic primitives
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@primitive
def set_(*args):
    """
    NOTE: This makes a set from args, but it has the property that when called with a string, it doesn't break
    the string into chars. So set('abc') = {'a', 'b', 'c'}, but set_('abc') = {'abc'}
    """
    out = set()
    for a in args:
        out.add(a)
    return out

@primitive
def set_add_(x,s):
    s.add(x)
    return s

@primitive
def union_(A,B): return A.union(B)

@primitive
def intersection_(A,B): return A.intersection(B)

@primitive
def setdifference_(A,B): return A.difference(B)

@primitive
def select_(A): # choose an element, but don't remove it

    try: # quick selecting without copying
        return set([next(iter(A))])
    except StopIteration:
        return set()

    #if len(A) > 0:
        #x = A.pop()
        #A.add(x)
        #return set([x]) # but return a set
    #else: return set() # empty set


@primitive
def issubset_(A, B): return A.issubset(B)

from random import sample as random_sample
@primitive
def sample_unique_(S):
    return random_sample(S,1)[0]

from random import choice as random_choice
@primitive
def sample_(S):
    if len(S) == 0: return set()
    else:           return random_choice(list(S))


@primitive
def exhaustive_(A,B): return coextensive(A,B)

@primitive
def coextensive_(A,B): return coextensive(A,B)
def coextensive(A,B): # are the two sets coextensive?
    #print A,B
    return (A.issubset(B) and B.issubset(A))

@primitive
def equal_(A,B): return (A == B)

@primitive
def equal_word_(A,B): return (A == B)

@primitive
def empty_(A): return (len(A)==0)

@primitive
def nonempty_(A): return (len(A) > 0)

@primitive
def cardinality1_(A): return (len(A)==1)

@primitive
def cardinality2_(A): return (len(A)==2)

@primitive
def cardinality3_(A): return (len(A)==3)

@primitive
def cardinality4_(A): return (len(A)==4)

@primitive
def cardinality5_(A): return (len(A)==5)

@primitive
def cardinality_(A): return len(A)

# returns cardinalities of sets and otherwise numbers -- for duck typing sets/ints
def cardify(x):
    if isinstance(x, set): return len(x)
    else: return x

@primitive
def cardinalityeq_(A,B): return cardify(A) == cardify(B)

@primitive
def cardinalitygt_(A,B): return cardify(A) > cardify(B)

@primitive
def cardinalitylt_(A,B): return cardify(A) > cardify(B)

@primitive
def subset_(A,B):
    return A.issubset(B)

@primitive
def is_in_(x,S):
    return (x in S)

@primitive
def diff_(S, p):
    """
    takes a set and an element of that set and
    returns the set minus that element
    """
    return S.difference(set(p))

@primitive
def range_set_(x, y, bound=Infinity):
    if y < x or y-x > bound or isnan(x) or isnan(y) or isinf(x) or isinf(y):
        return set()
    else:
        return set(range(x, y+1))


