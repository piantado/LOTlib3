from LOTlib3.Eval import primitive

import math
from numpy import sign

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PI = math.pi
TAU = 2.0*PI
E = math.e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Basic arithmetic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@primitive
def negative_(x): return -x
def neg_(x): return -x

@primitive
def plus_(x,y): return x+y

@primitive
def times_(x,y): return x*y

@primitive
def divide_(x,y):
    if y != 0.: return x/y
    else:     return float("inf")*x

@primitive
def subtract_(x,y): return x-y

@primitive
def minus_(x,y): return x-y

@primitive
def sin_(x):
    try:
        return math.sin(x)
    except: return float("nan")

@primitive
def cos_(x):
    try:
        return math.cos(x)
    except: return float("nan")

@primitive
def tan_(x):
    try:
        return math.tan(x)
    except: return float("nan")

@primitive
def sqrt_(x):
    try: return math.sqrt(x)
    except: return float("nan")

@primitive
def pow_(x,y):
    #print x,y
    try: return pow(x,y)
    except: return float("nan")

@primitive
def powf_(x,y):
    try: return pow(float(x),float(y))
    except: return float("nan")

@primitive
def ipowf_(x,y):
    try: return int(pow(float(x),float(y)))
    except: return float("nan")


@primitive
def abspow_(x,y):
    """ Absolute power. sign(x)*abs(x)**y """
    #print x,y
    try: return sign(x)*pow(abs(x),y)
    except: return float("nan")

@primitive
def exp_(x):
    try:
        r = math.exp(x)
        return r
    except:
        return float("inf")*x

@primitive
def abs_(x):
    try:
        r = abs(x)
        return r
    except:
        return float("inf")*x


@primitive
def log_(x):
    if x > 0: return math.log(x)
    else: return -float("inf")

@primitive
def log2_(x):
    if x > 0: return math.log(x)/math.log(2.0)
    else: return -float("inf")

@primitive
def pow2_(x):
    return math.pow(2.0,x)

@primitive
def mod_(x,y):
    if y==0.0 or math.isnan(x) or math.isnan(y):
        return float("nan")
    return x % y

@primitive
def gt_(x, y):
    return (x>y)

@primitive
def geq_(x, y):
    return (x>=y)


@primitive
def lt_(x, y):
    return (x<y)

@primitive
def leq_(x, y):
    return (x<=y)

@primitive
def eequals_(x, y, epsilon=0.0001):
    """
    Equals up to some epsilon
    """
    return abs(x-y) < epsilon