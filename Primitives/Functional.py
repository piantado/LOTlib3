from LOTlib3.Eval import primitive, RecursionDepthException
from LOTlib3.Miscellaneous import raise_exception

## TODO: Add transitive closure of an operation


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~ The Y combinator and a bounded version
# example:
# fac = lambda f: lambda n: (1 if n<2 else n*(f(n-1)))
# Y(fac)(10)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Y = lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)) )
MAX_RECURSION = 25

@primitive
def raise_exception(e):
    raise e

def Y_bounded(f):
    """
    A fancy fixed point iterator that only goes MAX_RECURSION deep, else throwing a a RecusionDepthException
    """
    return (lambda x, n: x(x, n))(lambda y, n: f(lambda *args: y(y, n+1)(*args))
                                  if n < MAX_RECURSION else raise_exception(RecursionDepthException), 0)


def Ystar(*l):
    """
    The Y* combinator for mutually recursive functions. Holy shit.

    (define (Y* . l)
          ((lambda (u) (u u))
            (lambda (p) (map (lambda (li) (lambda x (apply (apply li (p p)) x))) l))))

    See:
    http://okmij.org/ftp/Computation/fixed-point-combinators.html]
    http://stackoverflow.com/questions/4899113/fixed-point-combinator-for-mutually-recursive-functions

    E.g., here is even/odd:

    even,odd = Ystar( lambda e,o: lambda x: (x==0) or o(x-1), \
                          lambda e,o: lambda x: (not x==0) and e(x-1) )

        Note that we require a lambda e,o on the outside so that these can have names inside.
    """

    return (lambda u: u(u))(lambda p: [lambda x: apply(li, p(p))(x) for li in l])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lambda calculus & Scheme
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@primitive
def fold_(f, initial, lst):
    if len(lst) == 0:
        return initial
    else:
        return f( lst[0], fold_(f, initial, lst[1:]))

@primitive
def reverse_(lst):
    return lst[::-1]

@primitive
def lambda_(f,args):
    f.args = args
    return f

@primitive
def map_(f,A):
    return [f(a) for a in A]

@primitive
def apply_(f,*args):
    return f(*args)

@primitive
def cons_(x,y):
    return [x,y]

@primitive
def cdr_(x):
    try:    return x[1:]
    except IndexError: return []

@primitive
def rest_(x):
    return cdr_(x)

@primitive
def car_(x):
    try:    return x[0]
    except IndexError: return []

@primitive
def first_(x):
    return car_(x)

@primitive
def filter_(f,x):
    return list(filter(f,x))

@primitive
def filterset_(f,x):
    return set(filter(f,x))

@primitive
def mapset_(f,A):
    return {f(a) for a in A}

@primitive
def Ystar_(*args):
    return Ystar(*args)

from random import random

@primitive
def optional_(x, y):
    if random() < 0.5:
        return cons_(x,y)
    else:
        return y

@primitive
def geometric_(x,y):
    # geometric number of xes followed by y
    if random() < 0.5:
        return y
    else:
        return cons_(x, geometric_(x,y))

