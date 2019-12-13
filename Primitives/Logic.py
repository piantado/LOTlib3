from LOTlib3.Eval import primitive
import itertools

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Basic logic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@primitive
def id_(A): return A # an identity function

@primitive
def and_(A,B): return (A and B)

@primitive
def AandnotB_(A,B): return (A and (not B))

@primitive
def notAandB_(A,B): return ((not A) and B)

@primitive
def AornotB_(A,B): return (A or (not B))

@primitive
def A_(A,B): return A

@primitive
def notA_(A,B): return not A

@primitive
def B_(A,B): return B

@primitive
def notB_(A,B): return not B

@primitive
def nand_(A,B): return not (A and B)

@primitive
def or_(A,B): return (A or B)

@primitive
def nor_(A,B): return not (A or B)

@primitive
def xor_(A,B): return (A and (not B)) or ((not A) and B)

@primitive
def not_(A): return (not A)

@primitive
def implies_(A,B): return ((not A) or B)

@primitive
def iff_(A,B): return ((A and B) or ((not A) and (not B)))

@primitive
def if_(C,X,Y):
    if C: return X
    else: return Y

@primitive
def gt_(x,y): return x>y

@primitive
def gte_(x,y): return x>=y

@primitive
def lt_(x,y): return x<y

@primitive
def lte_(x,y): return x<=y

@primitive
def eq_(x,y): return x==y

@primitive
def zero_(x,y): return x==0.0


@primitive
def streq_(x,y): return str(x)==str(y)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Quantification
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@primitive
def not_exists_(F,S): return not exists_(F,S)

@primitive
def exists_(F,S): return exists(F,S)
def exists(F,S):
    return any(map(F,S)) # This appears to be faster than writing it ourself

@primitive
def not_forall_(F,S): return not forall(F,S)

@primitive
def forall_(F,S): return forall(F,S)

def forall(F,S):
    return all(map(F,S))

@primitive
def iota_(F,S):
    """
        The unique F in S. If none, or not unique, return None
    """
    match = None
    for s in S:
        if F(s):
            if match is None: match = s
            else: return None  # We matched more than one
    return match


