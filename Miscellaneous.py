# -*- coding: utf-8 -*-

"""
Miscellaneous functions for LOTlib3.

"""
# Special handling to deal with numpypy (which actually tends to be slower for LOTlib)
import collections
import math
from math import exp, log, pi, lgamma
from random import random, sample
import re
import os
import inspect
import sys
import getpass
import types    # For checking if something is a function: isinstance(f, types.FunctionType)

try: import numpy as np
except ImportError: import numpypy as np

# Some useful constants
Infinity = float("inf")
inf = Infinity
Inf = Infinity
Null = []
TAU = 6.28318530718     # fuck pi

# For R-friendly
T = True
F = False


#-------------------------------------------------------------------------------------------------------------
# self.__dict__.update creates a sesanmplf.self object. We want to pop this off!
# https://stackoverflow.com/questions/6025758/whats-the-pythonic-way-to-set-class-variables
def self_update(s,l):
    s.__dict__.update(l)
    s.__dict__.pop('self')
#_____________________________________________________________________________________________________________
# ------------------------------------------------------------------------------------------------------------

def first(x):
    return x[0]
def second(x):
    return x[1]
def third(x):
    return x[2]
def fourth(x):
    return x[3]
def fifth(x):
    return x[4]
def sixth(x):
    return x[5]
def seventh(x):
    return x[6]
def eighth(x):
    return x[7]


def dropfirst(g):
    """Yield all but the first in a generator."""
    keep = False
    for x in g:
        if keep: yield x
        keep = True        


def None2Empty(x):
    # Treat Nones as empty
    return [] if x is None else x


def make_mutable(x):
    # TODO: update with other types
    if isinstance(x, frozenset):
        return set(x)
    elif isinstance(x, tuple):
        return list(x)
    else: 
        raise NotImplementedError


def make_immutable(x):
    # TODO: update with other types
    if isinstance(x, set ):
        return frozenset(x)
    elif isinstance(x, list):
        return tuple(x)
    else:
        raise NotImplementedError


def unlist_singleton(x):
    """Remove any sequences of nested lists with one element.

    Example:
        [[[1,3,4]]] -> [1,3,4]

    """
    if isinstance(x,list) and len(x) == 1:
        return unlist_singleton(x[0])
    else:
        return x


def list2sexpstr(lst):
    """Prints a python list-of-lists as an s-expression.

    [['K', 'K'], [['S', 'K'], ['I', 'I']]] --> ((K K) ((S K)(I I)))

    """
    s = re.sub(r'[\'\",]', r'', str(lst))
    s = re.sub(r'\[', '(', s) # changed r'(' to '('
    s = re.sub(r'\]', ')', s) # changed r')' to ')'
    return s


# ------------------------------------------------------------------------------------------------------------
# Display functions
# ------------------------------------------------------------------------------------------------------------

def q(x, quote='\''):
    """Quotes a string."""
    if isinstance(x,str) or isinstance(x, str):
        return quote+x+quote
    else:
        return quote+str(x)+quote


def qq(x):
    return q(x,quote="\"")


def display(x):
    print(x)


# for functional programming, print something and return it
def printr(x):
    print(x)
    return x


def r2(x):
    return round(x,2)
def r3(x):
    return round(x,3)
def r4(x):
    return round(x,4)
def r5(x):
    return round(x,5)


def tf201(x):
    if x:
        return 1
    else:
        return 0


# Functions for I/O
def display_option_summary(obj):
    """Prints out a friendly format of all options -- for headers of output files.

    This takes in an OptionParser object as an argument. As in, (options, args) = parser.parse_args()

    """
    from time import strftime, time, localtime
    import os

    print("#"*90)
    try: print("# Username: ", getpass.getuser())
    except OSError: pass

    try: print("# Date: ", strftime("%Y %b %d (%a) %H:%M:%S", localtime(time()) ))
    except OSError: pass

    try:
        if sys.platform == 'win32': print("# Uname: Unavailable")
        else: print("# Uname: ", os.uname())
    except OSError: pass

    try: print("# Pid: ", os.getpid())
    except OSError: pass

    for slot in dir(obj):
        attr = getattr(obj, slot)
        if not isinstance(attr, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)) \
           and (slot != "__doc__") and (slot != "__module__"):
            print("#", slot, "=", attr)
    print("#"*90)


# ------------------------------------------------------------------------------------------------------------
# Genuine Miscellany
# ------------------------------------------------------------------------------------------------------------

def infrange(n=Infinity):
    """
    yields 0, 1, 2, 3, ...
    """
    i = 0
    while i<n:
        yield i
        i += 1

def takeN(g, n):
    for i, v in enumerate(g):
        if i >= n:
            break
        yield v

# a wrapper so we can call this in the below weirdo composition
def raise_exception(e):
    raise e


def ifelse(x,y,z):
    if x: return y
    else: return z


def unique(gen):
    """Make a generator unique, returning each element only once."""
    s = set()
    for gi in gen:
        if gi not in s:
            yield gi
            s.add(gi)

def UniquifyFunction(gen):
        """A decorator to make a function only return unique values."""
        def f(*args, **kwargs):
                for x in unique(gen(*args, **kwargs)):
                        yield x
        return f

def flatten(expr):
    """
            Flatten lists of lists, via stackoverflow
    """
    def flatten_(expr):
        #print 'expr =', expr
        if expr is None or not isinstance(expr, collections.Iterable) or isinstance(expr, str):
            yield expr
        else:
            for node in expr:
                #print node, type(node)
                if (node is not None) and isinstance(node, collections.Iterable) and (not isinstance(node, str)):
                    #print 'recursing on', node
                    for sub_expr in flatten_(node):
                        yield sub_expr
                else:
                    #print 'yielding', node
                    yield node

    return tuple([x for x in flatten_(expr)])


def flatten2str(expr, sep=' '):
    # if expr is None: return ''
    # else:
    #     tmp = ''
    #     expr = str(expr)
    #     for e in expr:
    #         if e == 'a' or e == 'b': tmp += e
    #     return tmp

    try:
        if expr is None: return ''
        else:            return sep.join(flatten(expr))
    except TypeError:
        print("Error in flatter2str:", expr)
        raise TypeError

def weave(*iterables):
    """
    Intersperse several iterables, until all are exhausted.
    This nicely will weave together multiple chains

    from: http://www.ibm.com/developerworks/linux/library/l-cpyiter/index.html
    """

    iterables = list(map(iter, iterables))
    while iterables:
        for i, it in enumerate(iterables):
            try:
                yield next(it)
            except StopIteration:
                del iterables[i]




def lazyproduct(iterators, restart_ith):
        """
            Compute a product of the iterators, without holding all of their values in memory.
            This requires a function restart_ith that returns a new (refreshed or restarted) version of the
            i'th iterator so we can start it anew

            for g in lazyproduct( [xrange(10), xrange(10)], lambda i: xrange(10)):
            	print g

        """

        iterators = list(map(iter, iterators))

        # initialize the state
        try:
            state = [next(it) for it in iterators]
            yield state
        except StopIteration:
            return

        while True:

            for idx in range(len(iterators)): # the "carry" loop
                try:
                    state[idx] = next(iterators[idx])
                    break # break the idx loop (which would process "carries")
                except StopIteration:

                    if idx == len(iterators)-1:
                        return
                    else:
                        # restart the current one and increment the next
                        # by NOT breaking here
                        iterators[idx] = iter(restart_ith(idx))
                        state[idx] = next(iterators[idx]) # reset this state (the next idx is increment on the next loop)

                        # and no break so we iterate the next
            yield state

# ------------------------------------------------------------------------------------------------------------
# Math functions
# ------------------------------------------------------------------------------------------------------------

def nicelog(x):
    if x > 0.:
        return log(x)
    else:
        return -Infinity

def logsumexp(v):
    """
            stable numerical computation of log(sum(exp(v)))
    """

    if len(v) == 0:
        return -Infinity
    else:
        m = max(v)
        if m == Infinity: # needed!
            return Infinity
        elif m == -Infinity:
            return -Infinity
        else:
            return m + log(sum([exp(x - m) for x in v]))

def lognormalize(v):
    return v - logsumexp(v)

def logplusexp(a, b):
    """
            Two argument version. No cast to numpy, so faster
    """
    m = max(a,b)
    return m+log(exp(a-m)+exp(b-m))


def log1mexp(a, epsilon=1e-6):
    """
            Computes log(1-exp(a)) according to Machler, "Accurately computing ..."
            Note: a should be a large negative value!
            epsilon -- count things > 0 by this much as zero
    """


    if abs(a) < epsilon: # close to zero up to numerical precision
        return -Infinity

    if a < -log(2.0):
        return log1p(-exp(a))
    else:
        return log(-expm1(a))


def beta(x):
    """ Here a is a vector (of ints or floats) and this computes the Beta normalizing function,"""
    return sum(lgamma(a) for a in x) - lgamma(float(sum(x)))


def normlogpdf(x, mu, sigma):
    """ The log pdf of a normal distribution """
    #print x, mu
    return math.log(math.sqrt(2. * pi) * sigma) - ((x - mu) * (x - mu)) / (2.0 * sigma * sigma)

def norm_lpdf_multivariate(x, mu, sigma):
    # Via http://stackoverflow.com/questions/11615664/multivariate-normal-density-in-python
    size = len(x)

    # some checks:
    if size != len(mu) or (size, size) != sigma.shape: raise NameError("The dimensions of the input don't match")
    det = np.linalg.det(sigma)
    if det == 0: raise NameError("The covariance matrix can't be singular")

    norm_const = - size*log(2.0*pi)/2.0 - log(det)/2.0
    #norm_const = 1.0/ ( math.pow((2*pi),float(size)/2) * math.pow(det,1.0/2) )
    x_mu = np.matrix(x - mu)
    inv = np.linalg.inv(sigma)
    result = -0.5 * (x_mu * inv * x_mu.T)
    return norm_const + result


def logrange(mn, mx, steps):
    """
            Logarithmically-spaced steps from mn to mx, with steps number inbetween
            mn - min value
            mx - max value
            steps - number of steps between. When 1, only mx is returned
    """
    mn = np.log(mn)
    mx = np.log(mx)
    r = np.arange(mn, mx-1e-5, (mx-mn)/(steps-1)) # 1e-5 for numerical precision; otherwise we may add an extra
    r = np.append(r, mx)
    return np.exp(r)


def geometric_ldensity(n,p):
    """ Log density of a geomtric distribution """
    return (n-1)*log(1.0-p)+log(p)

from math import expm1, log1p

def EV(fn, n_samples, *args):
    """
        Estimates (via sampling) the expected value of a function that returns
        a numerical value. Pass any args to specified function as additional args
        ex: EV(random.randint, 2, 5)
    """
    return np.average([fn(*args) for _ in range(n_samples)])


def argmax(lst):
    return max([(x,i) for i,x in enumerate(lst)])[1]


def logit(p):
    return log(p/(1.-p))
def ilogit(x):
    return 1./(1.+exp(-x))

# ------------------------------------------------------------------------------------------------------------
# Sampling functions
# ------------------------------------------------------------------------------------------------------------

def sample1(*args):
    return sample_one(*args)

def sample_one(*args):
    if len(args) == 1:
        return sample(args[0], 1)[0]     # use the list you were given
    else:
        return sample(args, 1)[0]       # treat the arguments as a list


def flip(p):
    return random() < p


# TODO: THIS FUNCTION SUCKS PLEASE FIX IT
# TODO: Change this so that if N is large enough, you sort
def weighted_sample(objs, N=1, probs=None, log=False, return_probability=False, returnlist=False, Z=None):
    """When we return_probability, it is *always* a log probability.

    Takes unnormalized probabilities and returns a list of the log probability and the object returnlist
    makes the return always a list (even if N=1); otherwise it is a list for N>1 only

    TODO: This can sometimes not return if there are tons of really tiny probs...

    Note:
        This now can take probs as a function, which is then mapped!

    """
    # Check how probabilities are specified either as an argument, or attribute of objs (either probability
    #  or log prob).  Note: This ALWAYS returns a log probability
    if len(objs) == 0: return None

    # Convert to support indexing if we need it
    if isinstance(objs, set):
        objs = list(objs)

    myprobs = None
    if probs is None:
        myprobs = [1.0] * len(objs)     # Sample uniform
    elif isinstance(probs, types.FunctionType):     # Note: this does not work for class instance methods
        myprobs = list(map(probs, objs))
    else:
        myprobs = list(map(float, probs))

    # Now normalize and run
    if Z is None:
        if log:
            Z = logsumexp(myprobs)
            assert Z > -Infinity
        else:
            Z = sum(myprobs)
            assert Z > 0


    # print len(myprobs), Z
    # print log, myprobs, Z
    out = []

    for n in range(N):
        r = random()
        for i in range(len(objs)):
            # Set r based on log domain  or  probability domain.
            r = r - exp(myprobs[i] - Z) if log else r - (myprobs[i]/Z)

            #print r, myprobs
            if r <= 0:
                if return_probability:
                    lp = 0
                    if log:
                        lp = myprobs[i] - Z
                    else:
                        lp = math.log(myprobs[i]) - math.log(Z)

                    out.append([objs[i], lp])
                    break
                else:
                    out.append(objs[i])
                    break

    if N == 1 and (not returnlist):
        return out[0]   # Don't give back a list if you just want one.
    else:
        return out

# ------------------------------------------------------------------------------------------------------------
# Lambda calculus
# ------------------------------------------------------------------------------------------------------------

# Some innate lambdas
def lambdaZero(*x): return 0
def lambdaOne(*x): return 1
def lambdaInfinity(*x): return Infinity
def lambdaMinusInfinity(*x): return -Infinity
def lambdaNull(*x): return []
def lambdaNone(*x): return None
def lambdaTrue(*x): return True
def lambdaFalse(*x): return False
def lambdaNAN(*x): return float("nan")
def lambdaException(*x):
    raise Exception()
def lambdaAssertFalse(*x):
    assert False

# ------------------------------------------------------------------------------------------------------------
# Sorting utilities
# ------------------------------------------------------------------------------------------------------------

def scramble_sort(lst, keyfunction):
    """This is a sort that randomizes order among the ones with equal keys.

    Steve says: 'I have no idea why this is here.'

    """
    keys = [(keyfunction(li), random(), li) for li in lst]
    
    return [x[2] for x in sorted(keys)]

# ------------------------------------------------------------------------------------------------------------
# Memoization
# ------------------------------------------------------------------------------------------------------------


def attrmem(aname):
    """
    Memoize a class function, saving the return value to X in @attrmem(X)

    :param f: a function to memoize
    :return: the memoized function

    Example:
        @attrmem('prior')
        def compute_prior(self, ...):
            ...
    will save every output of compute_prior to self.prior
    """
    def wrap1(f):

        def wrap2(self, *args, **kwargs):
            v = f(self, *args, **kwargs)
            setattr(self, aname, v)
            return v

        return wrap2

    return wrap1

# ------------------------------------------------------------------------------------------------------------
# Help with logging and IO
# ------------------------------------------------------------------------------------------------------------
import shutil

def setup_directory(path):
    # Create a directory for logging and output

    if os.path.exists(path):
        shutil.rmtree(path)

    os.mkdir(path)

# ------------------------------------------------------------------------------------------------------------
# Generic Equality - stolen from https://stackoverflow.com/questions/390250/
# ------------------------------------------------------------------------------------------------------------

class CommonEqualityMixin(object):

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

# ------------------------------------------------------------------------------------------------------------
# Partition function
# stolen from http://stackoverflow.com/questions/18503096/python-integer-partitioning-with-given-k-partitions
# ------------------------------------------------------------------------------------------------------------

def partitions(n,k,l=1):
    '''n is the integer to partition, k is the length of partitions, l is the min partition element size'''
    if k < 1:
        raise StopIteration
    if k == 1:
        if n >= l:
            yield (n,)
        raise StopIteration
    for i in range(l,n+1):
        for result in partitions(n-i,k-1,i):
            yield (i,)+result